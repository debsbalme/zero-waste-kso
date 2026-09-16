import re
from datetime import datetime

import pandas as pd

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials



SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]


# ============================================================
# AUTHENTICATION
# ============================================================

def get_google_services(credentials_dict):

    credentials = Credentials(
        token=credentials_dict["token"],
        refresh_token=credentials_dict.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=credentials_dict["client_id"],
        client_secret=credentials_dict["client_secret"],
        scopes=SCOPES,
    )

    slides_service = build(
        "slides",
        "v1",
        credentials=credentials,
    )

    drive_service = build(
        "drive",
        "v3",
        credentials=credentials,
    )

    return slides_service, drive_service

# ============================================================
# TEMPLATE COPY
# ============================================================

def copy_template(
    drive_service,
    template_id,
    client_name,
    output_folder_id=None,
):
    """
    Copy the Google Slides template and return the new presentation ID.
    """

    today = datetime.now().strftime("%Y-%m-%d")

    body = {
        "name": f"{client_name} - Maturity Matrix - {today}",
    }

    if output_folder_id:
        body["parents"] = [output_folder_id]

    copied_file = drive_service.files().copy(
        fileId=template_id,
        body=body,
        supportsAllDrives=True,
    ).execute()

    return copied_file["id"]


# ============================================================
# PRESENTATION HELPERS
# ============================================================

def get_slide_text(slide):
    """
    Extract all text from a Google Slides slide.
    """

    text_parts = []

    for element in slide.get("pageElements", []):
        shape = element.get("shape")

        if not shape:
            continue

        text = shape.get("text")

        if not text:
            continue

        for text_element in text.get("textElements", []):
            text_run = text_element.get("textRun")

            if text_run:
                text_parts.append(
                    text_run.get("content", "")
                )

    return "".join(text_parts)


def find_slide_by_placeholder(
    slides_service,
    presentation_id,
    placeholder,
):
    """
    Find the slide containing a particular placeholder.

    Returns the slide object ID.
    """

    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    for slide in presentation.get("slides", []):
        slide_text = get_slide_text(slide)

        if placeholder in slide_text:
            return slide["objectId"]

    raise ValueError(
        f"Could not find slide containing placeholder: {placeholder}"
    )


# ============================================================
# TEXT REPLACEMENT
# ============================================================

def replace_text_on_slide(
    slides_service,
    presentation_id,
    slide_id,
    replacements,
):
    """
    Replace placeholders ONLY on the specified slide.
    """

    requests = []

    for placeholder, value in replacements.items():

        if value is None:
            value = ""

        if isinstance(value, float) and pd.isna(value):
            value = ""

        requests.append(
            {
                "replaceAllText": {
                    "containsText": {
                        "text": placeholder,
                        "matchCase": True,
                    },
                    "replaceText": str(value),
                    "pageObjectIds": [slide_id],
                }
            }
        )

    if requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests},
        ).execute()


# ============================================================
# SLIDE DUPLICATION
# ============================================================

def duplicate_slide(
    slides_service,
    presentation_id,
    template_slide_id,
):
    """
    Duplicate a template slide and return the new slide ID.
    """

    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={
            "requests": [
                {
                    "duplicateObject": {
                        "objectId": template_slide_id
                    }
                }
            ]
        },
    ).execute()

    new_slide_id = (
        response["replies"][0]["duplicateObject"]["objectId"]
    )

    return new_slide_id


def delete_slide(
    slides_service,
    presentation_id,
    slide_id,
):
    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={
            "requests": [
                {
                    "deleteObject": {
                        "objectId": slide_id
                    }
                }
            ]
        },
    ).execute()


# ============================================================
# TEXT CLEANING
# ============================================================

def markdown_to_plain_text(text):
    """
    Very lightweight Markdown cleanup for Slides.
    """

    if not text:
        return ""

    text = str(text)

    # headings
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    # bold
    text = text.replace("**", "")

    # italics
    text = text.replace("*", "")

    # markdown bullets
    text = re.sub(
        r"^\s*-\s+",
        "• ",
        text,
        flags=re.MULTILINE,
    )

    return text.strip()


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

def populate_executive_summary(
    slides_service,
    presentation_id,
    executive_summary,
):
    slide_id = find_slide_by_placeholder(
        slides_service,
        presentation_id,
        "{{EXECUTIVE_SUMMARY}}",
    )

    replace_text_on_slide(
        slides_service,
        presentation_id,
        slide_id,
        {
            "{{EXECUTIVE_SUMMARY}}":
                markdown_to_plain_text(executive_summary)
        },
    )


# ============================================================
# MATURITY GAP SLIDES
# ============================================================

def create_gap_slides(
    slides_service,
    presentation_id,
    gaps_df,
):
    if gaps_df is None or gaps_df.empty:
        return

    required_columns = {
        "Category",
        "Heading",
        "Context",
        "Impact",
    }

    if not required_columns.issubset(gaps_df.columns):
        raise ValueError(
            "Gap DataFrame must contain: "
            "Category, Heading, Context, Impact"
        )

    template_slide_id = find_slide_by_placeholder(
        slides_service,
        presentation_id,
        "{{GAP_CATEGORY}}",
    )

    rows = gaps_df.to_dict("records")

    # ========================================================
    # STEP 1
    # Duplicate ALL required slides in ONE API call
    # ========================================================

    duplicate_requests = []

    for _ in rows:
        duplicate_requests.append({
            "duplicateObject": {
                "objectId": template_slide_id
            }
        })

    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": duplicate_requests},
    ).execute()

    # Get IDs of newly-created slides
    new_slide_ids = [
        reply["duplicateObject"]["objectId"]
        for reply in response["replies"]
    ]

    # Google inserts duplicates after the template.
    # Reverse to preserve dataframe ordering.
    new_slide_ids.reverse()

    # ========================================================
    # STEP 2
    # Populate ALL slides in ONE API call
    # ========================================================

    populate_requests = []

    for slide_id, row in zip(new_slide_ids, rows):

        replacements = {
            "{{GAP_CATEGORY}}":
                row.get("Category", ""),

            "{{HEADING}}":
                row.get("Heading", ""),

            "{{CONTEXT}}":
                row.get("Context", ""),

            "{{IMPACT}}":
                row.get("Impact", ""),
        }

        for placeholder, value in replacements.items():

            if value is None:
                value = ""

            if isinstance(value, float) and pd.isna(value):
                value = ""

            populate_requests.append({
                "replaceAllText": {
                    "containsText": {
                        "text": placeholder,
                        "matchCase": True,
                    },
                    "replaceText": str(value),
                    "pageObjectIds": [slide_id],
                }
            })

    # Also delete the blank template
    populate_requests.append({
        "deleteObject": {
            "objectId": template_slide_id
        }
    })

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": populate_requests},
    ).execute()



# ============================================================
# MATURITY DRIVER SLIDES
# ============================================================

def create_driver_slides(
    slides_service,
    presentation_id,
    drivers_df,
):
    if drivers_df is None or drivers_df.empty:
        return

    required_columns = {
        "Category",
        "Heading",
        "Context",
        "Impact",
    }

    if not required_columns.issubset(drivers_df.columns):
        raise ValueError(
            "Driver DataFrame must contain: "
            "Category, Heading, Context, Impact"
        )

    template_slide_id = find_slide_by_placeholder(
        slides_service,
        presentation_id,
        "{{DRIVER_CATEGORY}}",
    )

    rows = drivers_df.to_dict("records")

    # ========================================================
    # STEP 1
    # Duplicate all driver slides
    # ========================================================

    duplicate_requests = []

    for _ in rows:
        duplicate_requests.append({
            "duplicateObject": {
                "objectId": template_slide_id
            }
        })

    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": duplicate_requests},
    ).execute()

    new_slide_ids = [
        reply["duplicateObject"]["objectId"]
        for reply in response["replies"]
    ]

    new_slide_ids.reverse()

    # ========================================================
    # STEP 2
    # Populate all driver slides
    # ========================================================

    populate_requests = []

    for slide_id, row in zip(
        new_slide_ids,
        rows,
    ):

        replacements = {
            "{{DRIVER_CATEGORY}}":
                row.get("Category", ""),

            "{{HEADING}}":
                row.get("Heading", ""),

            "{{CONTEXT}}":
                row.get("Context", ""),

            "{{IMPACT}}":
                row.get("Impact", ""),
        }

        for placeholder, value in replacements.items():

            if value is None:
                value = ""

            if isinstance(value, float) and pd.isna(value):
                value = ""

            populate_requests.append({
                "replaceAllText": {
                    "containsText": {
                        "text": placeholder,
                        "matchCase": True,
                    },
                    "replaceText": str(value),
                    "pageObjectIds": [slide_id],
                }
            })

    # Delete original blank template
    populate_requests.append({
        "deleteObject": {
            "objectId": template_slide_id
        }
    })

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": populate_requests},
    ).execute()

# ============================================================
# MAIN REPORT FUNCTION
# ============================================================

def create_maturity_presentation(
    credentials_dict,
    template_id,
    client_name,
    executive_summary,
    gaps_df,
    drivers_df,
    output_folder_id=None,
):

    slides_service, drive_service = get_google_services(
        credentials_dict
)

    verify_drive_access(
        drive_service=drive_service,
        template_id=template_id,
        output_folder_id=output_folder_id,
)
    # ----------------------------------------
    # Create copy of template
    # ----------------------------------------

    presentation_id = copy_template(
        drive_service=drive_service,
        template_id=template_id,
        client_name=client_name,
        output_folder_id=output_folder_id,
    )

    # ----------------------------------------
    # Client name
    # ----------------------------------------

    client_slide_id = find_slide_by_placeholder(
        slides_service,
        presentation_id,
        "{{CLIENT_NAME}}",
    )

    replace_text_on_slide(
        slides_service,
        presentation_id,
        client_slide_id,
        {
            "{{CLIENT_NAME}}": client_name
        },
    )

    # ----------------------------------------
    # Executive Summary
    # ----------------------------------------

    populate_executive_summary(
        slides_service,
        presentation_id,
        executive_summary,
    )

    # ----------------------------------------
    # Gaps
    # ----------------------------------------

    create_gap_slides(
        slides_service,
        presentation_id,
        gaps_df,
    )

    # ----------------------------------------
    # Drivers
    # ----------------------------------------

    create_driver_slides(
        slides_service,
        presentation_id,
        drivers_df,
    )

    # ----------------------------------------
    # Return result
    # ----------------------------------------

    return {
        "presentation_id": presentation_id,
        "url": (
            "https://docs.google.com/presentation/d/"
            f"{presentation_id}/edit"
        ),
    }

def verify_drive_access(
    drive_service,
    template_id,
    output_folder_id=None,
):
    """
    Verify that the service account can access the
    template and optional output folder.
    """

    results = {}

    # -----------------------------
    # Template
    # -----------------------------

    try:
        template = drive_service.files().get(
            fileId=template_id,
            fields="id,name,mimeType",
            supportsAllDrives=True,
        ).execute()

        results["template"] = template

    except Exception as e:
        raise RuntimeError(
            "The Google service account cannot access "
            f"the Slides template.\n\n"
            f"Template ID: {template_id}\n\n"
            "Make sure the template is a native Google Slides "
            "presentation and is shared with the service-account "
            "email address.\n\n"
            f"Google error: {e}"
        )

    # -----------------------------
    # Output folder
    # -----------------------------

    if output_folder_id:

        try:
            folder = drive_service.files().get(
                fileId=output_folder_id,
                fields="id,name,mimeType",
                supportsAllDrives=True,
            ).execute()

            if folder.get("mimeType") != \
                    "application/vnd.google-apps.folder":

                raise RuntimeError(
                    f"SLIDES_OUTPUT_FOLDER_ID is not a folder. "
                    f"Google returned: {folder.get('name')}"
                )

            results["folder"] = folder

        except Exception as e:
            raise RuntimeError(
                "Your Google account cannot access "
                f"the output folder.\n\n"
                f"Folder ID: {output_folder_id}\n\n"
                f"Google error: {e}"
            )

    return results    