import pandas as pd
import json
import math # For math.isnan to check for NaN values
import openai
import streamlit as st
import ast
import re
from fpdf import FPDF

# Define the Recommendation Set as provided in your agent's internal knowledge base
RECOMMENDATION_SET = [
    {
        "question": "which automated bidding strategies have you used in dv360? please give further context of the performance in the comments section.",
        "answer": "n/a",
        "recommendation": "Utilize automated bidding strategies in DV360 to improve campaign agility.",
        "overview": "Automated bidding in DV360 leverages machine learning to optimize bids in real-time based on various signals like audience, device and contextual data, aligned with business goals like CPA or ROAS.",
        "gmpimpact": "Implementing automated bidding strategies increases the bidding precision with DV360 and reduces optimization overheads, while aligning campaign delivery with performance goals.",
        "businessimpact": "Automated bidding strategies provide an additional avenue for advertisers to drive better outcomes across programmatic investments with less manual intervention and improved campaign agility."
        
    },
    {
        "question": "have you developed or used any of the following custom bidding algorithms in dv360? please give further context of the objectives and performance in the comments section.",
        "answer": "n/a",
        "recommendation": "Utilize custom bidding strategies in DV360 to improve campaign agility",
        "overview": "Custom Bidding in DV360 allows advertisers to build their own bidding algorithms tailored to very specific high-value performance objectives, assigning custom signals such as Floodlight variables or Google Analytics goals to hit campaign targets.",
        "gmpimpact": "Custom Bidding leverages Google's bidding infrastructure while using advertiser-defined logic, enhancing optimization precision, integrating unique data and logic and directly aligning campaign delivery with unique business objectives.",
        "businessimpact": "This drives superior media performance and improves alignment between media investment and business priorities, whilst fostering campaign agility for maximized marketing effectiveness."
    },
    {
        "question": "which automated bidding strategies have you used in sa360?",
        "answer": "n/a",
        "recommendation": "Utilize automated bidding strategies in SA360 to improve campaign agility",
        "overview": "Search Ads 360 offers automated bidding solutions that use historical performance and real-time auction signals to optimize bids across search engines to meet specific business objectives.",
        "gmpimpact": "Implementing automated bidding strategies increases the bidding precision with SA360 and reduces optimization overheads, while aligning campaign delivery with performance goals.",
        "businessimpact": "Automated bidding strategies provide an additional avenue for advertisers to drive better outcomes across search investments with less manual intervention and improved campaign agility."

    },
    {
        "question": "have you used any of the cm360's apis? if so, please provide additional detail in the comments box.",
        "answer": "n/a",
        "recommendation": "Utilize CM360 APIs for increased productivity",
        "overview": "Campaign Manager 360 (CM360) APIs allow for automated campaign trafficking, reporting and creative management, increasing operational efficiency, data access and insight generation.",
        "gmpimpact": "Increase the productivity and agility of CM360, enhancing the flow of data between wider GMP products and external platforms, whilst minimizing the requirement for manual intervention.",
        "businessimpact": "Faster execution and deeper insights leading to quicker optimizations, reduced setup time and higher productivity, allowing existing resource to focus on driving innovation."      
    },
    {
        "question": "have you used sa360's api for campaign management and reporting automation? if so, please provide additional detail in the comments box.",
        "answer": ["no - we are currently not using sa360 apis","n/a"],
        "recommendation": "Utilize SA360 APIs for increased productivity",
        "overview": "SA360 APIs provide automated control over search campaigns, allowing bulk edits, custom reporting and integration with internal tools for optimization and analysis.",
        "gmpimpact": "Increase the productivity of SA360, streamlining campaign management and enhancing the flow of data between wider GMP products and external platforms. ",
        "businessimpact": "Enhanced automation improves agility and control over search campaigns translate into faster optimizations, increased performance and reduced operational costs."
    },
    {
        "question": "have you used dv360's api for campaign management and reporting automation? if so, please provide additional detail in the comments box.",
        "answer": "n/a",
        "recommendation": "Utilize DV360 APIs for increased productivity",
        "overview": "DV360 APIs provide advertisers automated control to manage and optimize campaigns, targeting, creatives and reporting.",
        "gmpimpact": "Increase the productivity of DV360, scaling optimizations, creating dynamic campaign adjustments and more agile media buying.",
        "businessimpact": "Enhanced automation improves the speed of campaign execution and accuracy, resulting in greater operational scale and stronger campaign performance."
    },
    {
        "question": "how are you activating first party data within dv360?",
        "answer": "n/a",
        "recommendation": "Utilize 1PD in DV360 for stronger data-driven optimization",
        "overview": "DV360 allows advertisers to onboard and activate 1st-party data such as CRM lists and site activity to inform and enhance audience targeting, bidding and measurement. Further solutions such as Google's Customer Match can also be utilized ",
        "gmpimpact": "Bringing 1st-party data in to DV360 unlocks additional platform features and capabilities (such as Customer Match) increasing the utilization of DV360. ",
        "businessimpact": "Linking 1PD sources to media activation results in higher-quality targeting and greater business outcomes from programmatic investments, with advertisers experiencing on average 2x revenue uplift. "   
    },
    {
        "question": "how are you activating first party data within sa360?",
        "answer": "n/a",
        "recommendation": "Utilize 1PD in SA360 for stronger data-driven optimization",
        "overview": "SA360 supports the integration of 1st-party data to inform bid strategies, audience targeting, and performance measurement across search campaigns.",
        "gmpimpact": "Bringing 1st-party data in to SA360 unlocks additional platform features and capabilities, increasing the utilization of SA360.",
        "businessimpact": "Stronger data-driven optimization results in more efficient budget use, higher-quality traffic, and greater business outcomes from paid search investments."        
    },
    {
        "question": "how are you activating first party data within cm360?",
        "answer": "n/a",
        "recommendation": "Utilize 1PD in CM360 for enhanced insight of customer interactions and segmentation",
        "overview": "CM360 supports the use of 1st-party data through floodlight activities and audience lists for more accurate measurement, tracking and attribution. This results in enriched reporting and campaign performance analysis.",
        "gmpimpact": "Integrating 1st-party data into CM360 unlocks additional platform capabilities and enhances cross-channel measurement, custom audience segments and provides more meaningful attribution and post-campaign analysis.",
        "businessimpact": "Improved marketing effectiveness through clearer performance insights, better-informed media decisions and a more holistic understanding of customer interactions across media touchpoints."
    },
    {
        "question": "is your instance of google tag manager server-side or client-side?",
        "answer": "gtm (client-side)",
        "recommendation": "Consider implementing server-side Google Tag Manager (sGTM) for increased data accuracy and control.",
        "overview": "Server-side tagging involves routing tag calls through a server rather than directly from a user's browser, improving load speed, data security, and privacy compliance.",
        "gmpimpact": "A forward thinking & futureproofed utilization of GMP, as server-side tagging ensures more complete, accurate and consistent data signals with more advertiser control over data sharing.",
        "businessimpact": "Improved data quality with more control, resulting in a more futureproofed tag management set-up in a changing regulatory landscape."
    },
    {
        "question": "which of the following google products are linked to your google analytics instance (ga4/ga360)?",
        "answer": "n/a",
        "recommendation": "Leverage Google Cloud and existing GMP investments for advanced audience modelling, insights and streamlined activation",
        "overview": "Leverage Google Cloud and the existing Google Marketing Platform investments to create a single solution for data storage, modelling & analysis, resulting in a more cost-efficient advanced audience strategy.",
        "gmpimpact": "Enhance the connectivity between existing Google platforms in place and enable more effective cross-channel targeting, insights & measurement.",
        "businessimpact": "Optimize the overarching platforms architecture, utilizing existing Google platforms for advanced audience strategy, increasing ROI of MarTech investment."        
    },
    {
        "question": "are your platforms set-up to test privacy sandbox apis (such as protected audience api, topics api, attribution reporting api etc)",
        "answer": [
            "yes but we have not begun testing any google privacy sandbox apis",
            "no we have not tested any google privacy sandbox apis, but we would like to understand what is applicable to our business"
        ],
        "recommendation": "Explore Privacy Sandbox API testing, further adapting a changing regulatory landscape",
        "overview": "Privacy Sandbox is Google's initiative to develop privacy-preserving alternatives for 3rd party cookies and cross-site tracking. APIs like Topics, Attribution Reporting, Private Aggregation and Protected Audience are designed to enable advertising functionalities while minimizing user data exposure.",
        "gmpimpact": "Exploring and testing Privacy Sandbox APIs is a key step in Google advertisers preparing for continued user privacy changes while maintaining critical functions such as frequency capping, remarketing, and attribution.",
        "businessimpact": "Proactively exploring and adopting privacy-safe tools aids with media activation & strategy continuity, compliance, and sustained campaign performance in a changing regulatory landscape."        
    },
    {
        "set_id": "bigquery",
        "questions": [
            {
                "question": "is bigquery in use for warehousing ga4/ga360 data?",
                "answer": "no"
            },
            {
                "question": "which google products are currently being utilized?",
                "answer": [
                    "google analytics 4 (ga4)",
                    "google analytics 360 (ga360)"
                ]
            },
        ],
        "recommendation": "Consider utilizing BigQuery for warehousing of data",
        "overview": "BigQuery is Google Cloud's data warehouse. Utilizing BigQuery enables advertisers to store, unify and analyze 1st-party, GMP and external data in one environment. Data stored in BigQuery can be stored in perpetuity while GA4 stores data for a maximum of 14 months.",
        "gmpimpact": "BigQuery integrates natively with GMP tools, including GA4, DV360, SA360, and CM360, unlocking use cases like improved data storage, predictive modeling, audience segmentation and deeper attribution analysis.",
        "businessimpact": "Utilization of BigQuery can enhance data-driven decision-making and supports long-term business intelligence strategies that enhance customer value and marketing performance."
    },
    {
        "set_id": "adh",
        "questions": [
            {
                "question": "which google products are currently being utilized?",
                "answer": "ads data hub (adh)"
            },
            {
                "question": "to what extent is ads data hub (adh) currently being used by your team(s) for measurement and analysis?",
                "answer": [
                    "we haven't used adh yet but are interested",
                    "we've used it a few times for exploratory or one-off analysis",
                    "we actively use adh for campaign measurement or insights"
                ]
            },
            {
                "question": "in addition to what is currently being utilized what custom adh analysis would you like to undertake ? select all that apply",
                "answer": [
                    "reach & frequency",
                    "audience overlap",
                    "conversion lift",
                    "path to conversion",
                    "other"
                ]
            }
        ],
        "recommendation": "Consider deployment of enhanced hands-on optimization strategy within Ads Data Hub (ADH)",
        "overview": "Deploy hands-on optimization strategy within ADH, enhancing the efficiency and output quality of use cases when utilizing Google's wall-garden clean room.",
        "gmpimpact": "Increase the value derived from ADH and related GMP ecosystem, through enhanced utilization of its functionalities and measurement mechanisms.",
        "businessimpact": "More efficient and reliable reporting & measurement outcomes, improving the proven marketing ROI."        
    },
    {
        "set_id": "ga4imp",
        "questions": [
            {
                "question": "which google products are currently being utilized?",
                "answer": [
                    "google analytics 4 (ga4)",
                    "google analytics 360 (ga360)"
                ]
            },
            {
                "question": "do you have ga4/ga360 maintenance in place: tagging, refreshing internal filters, updating channel groupings, reevaluating audiences and segments, etc?",
                "answer": [
                    "platform maintenance processes are implemented but not regularly followed",
                    "no platform maintenance takes place"
                ]
            },
            {
                "question": "which of the following best describes the way you use data in ga4/ga360?",
                "answer": ["we collect pageviews and sporadic event data. we regularly leverage the built-in ga4 reports to gain insights about our customers, improve website/app user experience and campaign performance.",
                    "we collect only high-level website data and periodically review the basic metics (i.e. page views, unique visitors, bounce rate, top viewed pages) to monitor performance.",
                    "we have it set up but it is currently not being utilized."
                ]
            }
        ],
        "recommendation": "Consider GA4 audit of platform implementation & maintenance to increase on-site insights and a more advanced audience strategy",
        "overview": "GA4 provides cross-platform analytics with advanced event tracking, predictive metrics, advanced audience tools and seamless integration with the wider GMP suite. An audit of GA4 implementation and maintenance ensures correct setup and ongoing data quality.",
        "gmpimpact": "Auditing and properly maintaining GA4 ensures accurate, holistic data collection that enhances customer insights and audience strategy, whilst also improving the utilization of wider GMP products such as media activation and website and app performance analysis.",
        "businessimpact": "Reliable GA4 implementation and maintenance supports enhanced insights, a more effective audience strategy and increased return on investment in wider GMP products."
    },
    {
        "set_id": "enhancedconv",
        "questions": [
            {
                "question": "what industry is the brand considered to be in?",
                "answer": [
                    "chemical",
                    "education",
                    "government",
                    "healthcare",
                    "legal",
                    "military",
                    "pharmaceuticals",
                    "toys",
                    "other",
                    "n/a"
                ],
                "type": "negative_choice"
            },
            {
                "question": "have you implemented conversion api's (capi)? if so please specify across which partners capis have been implemented.",
                "answer": [
                    "google enhanced conversions",
                    "google enhanced conversions for leads"
                 ],
                "type": "negative_choice"
            },
            {
                "question": "what google owned & operated inventory is currently being bought in media campaigns?",
                "answer": [
                    "google search",
                    "youtube"
                ]
            },
            {
                "question": "do any of your media campaign conversion points involve the customer sharing pii?",
                "answer": [
                    "yes - at point of conversion we collect advance crm: name, address, email, tel, post code, customerid, maid and more",
                    "yes - at point of conversion we collect basic crm: email and/or maid only"
                ]
            },
            {
                "question": "what are your media campaign goals?",
                "answer": [
                    "acquisition",
                    "direct response",
                    "lead generation",
                    "retention",
                    "sales"
                ]
            }
        ],
        "recommendation": "Implement Google's Enhanced Conversions for more complete conversion data capture",
        "overview": "Enhanced Conversions is a solution that improves the accuracy of conversion measurement by securely using hashed first-party data to match conversions to ad interactions. This helps recover conversions that may not be tracked due to browser limitations or user privacy settings.",
        "gmpimpact": "Implementing Enhanced Conversions will allow the advertiser to capture more complete conversion data, improving the reliability of attribution and automated bidding capabilities in Google Ads and SA360.",
        "businessimpact": "Implementation of Enhanced Conversions will lead to smarter bidding decisions, improved ROI and stronger confidence in marketing spend."
     },
    {
        "set_id": "GCPCDP",
        "questions": [
            {
                "question": "which of the following best describes the types of platforms your organize uses to manage first-party data? select all that apply",
                "answer": [
                    "customer data platform (cdp)"
                ],
                "type": "negative_choice"
            },
            {
                "question": "which google products are currently being utilized?",
                "answer": [
                    "google ads",
                    "display & video 360 (dv360)",
                    "search ads 360 (sa360)"
                ]
            },
            {
                "question": "which google products are currently being utilized?",
                "answer": [
                    "google analytics 4 (ga4)",
                    "google analytics 360 (ga360)"
                ]
            },
            {
                "question": "which google products are currently being utilized?",
                "answer": [
                    "bigquery"
                ]
            },
            {
                "question": "is bigquery in use for warehousing ga4/ga360 data?",
                "answer": [
                    "yes"
                ]
            },
            {
                "question": "approximately what % of the next 12 months media budget is to be allocated to gmp platforms? give answer in percentages 0-100%",
                "answer": [
                    "50-75%",
                    "75-100%"
                ]
            }
        ],
        "recommendation": "Leverage Google Cloud and existing GMP investments for advanced audience modelling, insights and streamlined activation",
        "overview": "Leverage Google Cloud and the existing Google Marketing Platform investments to create a single solution for data storage, modelling & analysis, resulting in a more cost-efficient advanced audience strategy.",
        "gmpimpact": "Enhance the connectivity between existing Google platforms in place and enable more effective cross-channel targeting, insights & measurement. ",
        "businessimpact": "Optimize the overarching platforms architecture, utilizing existing Google platforms for advanced audience strategy, increasing ROI of MarTech investment."
    },
    {
        "set_id": "GCPClean",
        "questions": [
            {
                "question": "which of the following data usage activities does your organization currently engage or see value in? select all that apply",
                "answer": [
                    "not currently collaborating or sharing data",
                    "n/a"
                ],
                "type": "negative_choice"
            },
            {
                "question": "how important is data privacy and control when sharing data with external platforms, vendors and partners?",
                "answer": [
                    "very important, data must stay governed and secure at all times",
                    "mostly important, we prefer privacy controls but allow some flexibility",
                    "somewhat important, depends on the partner or use case",
                ]
            }
        ],
        "recommendation": "Consider utilization of GCP data cleanroom for secure data processing and collaboration",
        "overview": "A data cleanroom on GCP allows secure data collaboration between the advertiser and partners (e.g., Google, retailers, publishers) without exposing user-level information.",
        "gmpimpact": "The GCP cleanroom can enable use cases including audience syndication and audience enrichment, as well as analytics use cases such as incrementality and partner overlap without violating data privacy.",
        "businessimpact": "This delivers stronger insights into media effectiveness, partner value and multi-touch attribution, enabling more strategic media planning and increased privacy controls over data sharing."
    }
]

def normalize_answer_for_comparison(answer_value):
    """
    Helper function to normalize answers consistent with agent's rules.
    Used for both CSV answers and Recommendation Set answers.
    """
    if pd.isna(answer_value):
        return ""

    normalized_val = str(answer_value).lower().strip()

    if normalized_val == 'n/a' or normalized_val == '':
        return ""

    return normalized_val

def run_recommendation_analysis(df):
    """
    Executes the AI Agent's logic to process DataFrame data, match recommendations,
    and calculate total scores and max weights.
    Returns a dictionary containing matched recommendations and summary totals.
    """
    csv_data_map = {}
    for index, row in df.iterrows():
        question_key = str(row['Question']).lower().strip()
        answer_value = normalize_answer_for_comparison(row['Answer'])

        score = row['Score'] if pd.notna(row['Score']) else 0.0
        max_weight = row['MaxWeight'] if pd.notna(row['MaxWeight']) else 0.0

        score = max(0.0, float(score))
        max_weight = max(0.0, float(max_weight))

        # Handle multiple answers from CSV for the same question by storing them as a list
        if question_key not in csv_data_map:
            csv_data_map[question_key] = {
                'answers': [answer_value],
                'score': score,
                'maxweight': max_weight
            }
        else:
            csv_data_map[question_key]['answers'].append(answer_value)


    matched_recommendations_with_scores = []
    total_matched_recommendations = 0
    total_score = 0.0
    total_max_score = 0.0

    for item in RECOMMENDATION_SET:
        if "set_id" not in item:
            # A. Single Question Recommendation
            rec_question = item['question'].lower().strip()
            rec_answer_raw = item['answer']
            rec_recommendation = item['recommendation']
            rec_overview = item.get('overview', 'N/A')
            rec_gmp_impact = item.get('gmpimpact', 'N/A')
            rec_business_impact = item.get('businessimpact', 'N/A')
            rec_type = item.get('type')

            csv_entry = csv_data_map.get(rec_question)
            user_answers_from_csv = csv_entry['answers'] if csv_entry else [] # Get list of answers

            current_condition_met = False
            question_score_to_add = 0.0
            question_max_weight_to_add = 0.0

            if user_answers_from_csv: # Check if there are answers from CSV
                normalized_rec_answers = []
                if isinstance(rec_answer_raw, list):
                    normalized_rec_answers = [normalize_answer_for_comparison(val) for val in rec_answer_raw]
                else:
                    normalized_rec_answers = [normalize_answer_for_comparison(rec_answer_raw)]

                if rec_type == "negative_choice":
                    # For negative_choice, the condition is met if NONE of the user's answers are in the specified list
                    current_condition_met = all(user_ans not in normalized_rec_answers for user_ans in user_answers_from_csv)
                else:
                    # For positive choice (default), the condition is met if ANY of the user's answers are in the specified list
                    current_condition_met = any(user_ans in normalized_rec_answers for user_ans in user_answers_from_csv)


                if current_condition_met and csv_entry: # Also check if csv_entry exists before accessing score/maxweight
                    # If the condition is met, use the score and maxweight from the CSV row corresponding to this question.
                    question_score_to_add = csv_entry.get('score', 0.0)
                    question_max_weight_to_add = csv_entry.get('maxweight', 0.0)


            if current_condition_met:
                matched_recommendations_with_scores.append({
                    'recommendation': rec_recommendation,
                    'overview': rec_overview,
                    'gmp_impact': rec_gmp_impact,
                    'business_impact': rec_business_impact,
                    'score': question_score_to_add,
                    'maxweight': question_max_weight_to_add
                })
                total_matched_recommendations += 1
                total_score += question_score_to_add
                total_max_score += question_max_weight_to_add

        else:
            # B. Grouped Questions Recommendation
            all_sub_questions_match = True
            group_questions = item['questions']
            group_recommendation = item['recommendation']
            rec_overview = item.get('overview', 'N/A')
            rec_gmp_impact = item.get('gmpimpact', 'N/A')
            rec_business_impact = item.get('businessimpact', 'N/A')

            current_group_contributing_scores = 0.0
            current_group_contributing_max_weights = 0.0

            for sub_q_item in group_questions:
                sub_q_question = sub_q_item['question'].lower().strip()
                sub_q_answer_raw = sub_q_item['answer']
                sub_q_type = sub_q_item.get('type')

                csv_sub_q_entry = csv_data_map.get(sub_q_question)
                user_answers_from_csv_sub_q = csv_sub_q_entry['answers'] if csv_sub_q_entry else [] # Get list of answers

                current_sub_q_condition_met = False

                if user_answers_from_csv_sub_q: # Check if there are answers from CSV for sub-question
                    normalized_sub_q_answers = []
                    if isinstance(sub_q_answer_raw, list):
                        normalized_sub_q_answers = [normalize_answer_for_comparison(val) for val in sub_q_answer_raw]
                    else:
                        normalized_sub_q_answers = [normalize_answer_for_comparison(sub_q_answer_raw)]

                    if sub_q_type == "negative_choice":
                         # For negative_choice, the condition is met if NONE of the user's answers are in the specified list
                        current_sub_q_condition_met = all(user_ans not in normalized_sub_q_answers for user_ans in user_answers_from_csv_sub_q)
                    else:
                        # For positive choice (default), the condition is met if ANY of the user's answers are in the specified list
                        current_sub_q_condition_met = any(user_ans in normalized_sub_q_answers for user_ans in user_answers_from_csv_sub_q)

                # If any sub-question condition is NOT met, the entire group condition fails
                if not current_sub_q_condition_met:
                    all_sub_questions_match = False
                    break # Exit the inner loop as the group condition has failed
                else:
                    # If the sub-question condition IS met, add its score and maxweight
                    if csv_sub_q_entry:
                        current_group_contributing_scores += csv_sub_q_entry.get('score', 0.0)
                        current_group_contributing_max_weights += csv_sub_q_entry.get('maxweight', 0.0)


            # After checking all sub-questions, if all matched, add the group recommendation
            if all_sub_questions_match:
                matched_recommendations_with_scores.append({
                    'recommendation': group_recommendation,
                    'overview': rec_overview,
                    'gmp_impact': rec_gmp_impact,
                    'business_impact': rec_business_impact,
                    'score': current_group_contributing_scores,
                    'maxweight': current_group_contributing_max_weights
                })
                total_matched_recommendations += 1
                total_score += current_group_contributing_scores
                total_max_score += current_group_contributing_max_weights

    return {
        'matched_recommendations': matched_recommendations_with_scores,
        'total_matched_recommendations': total_matched_recommendations,
        'total_score': total_score,
        'total_max_score': total_max_score
    }

# (Keep your RECOMMENDATION_SET and normalize_answer_for_comparison function here)

# Place run_recommendation_analysis() function here

# === Step 1: Calculate Maturity Levels ===
#def calculate_maturity_levels(df):
#    category_maturity = df.groupby("Category").agg(
#        total_score=pd.NamedAgg(column="Score", aggfunc="sum"),
#        total_max_weight=pd.NamedAgg(column="MaxWeight", aggfunc="sum")
   # )
#    category_maturity["maturity_level"] = (category_maturity["total_score"] / category_maturity["total_max_weight"] * 100).round(2)
#    return category_maturity.reset_index()


# === Step 2: Generate Category Summaries with GPT ===
def generate_category_summary(df):
 
    subset = df
    categories = subset["Category"].tolist()
    questions = subset["Question"].tolist()
    answers = subset["Answer"].tolist()
    comments = subset["Comment"].fillna("").tolist() if "Comment" in df.columns else []

    prompt = f"""
    You are a strategic Adtech/Martech advisor assessing an advertiser’s maturity based on their audit responses
    Provide a summary using the answers and comments for all questions focusing on their current usage marketing maturity in their implementation for Adtech and Martech.
    Provide the response in a set of bullet points, these will be emailed and need to be understand by sales, marketing and adtech colleagues.
    Please provide the summary for eacg of the categories provided.
    Categories: {categories}
    Questions: {questions}
    Answers: {answers}
    Comments: {comments}
    """

    client = openai.OpenAI(api_key=st.secrets["OPEN_AI_KEY"])
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Imagine you are a marketing agency focused on Adtech and Martech and Google Marketing Platform."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )

    summary = response.choices[0].message.content
    return summary

def generate_bullet_summary(df):
    
    subset = df
    categories = subset["Category"].tolist()
    questions = subset["Question"].tolist()
    answers = subset["Answer"].tolist()
    comments = subset["Comment"].fillna("").tolist() if "Comment" in df.columns else []

    prompt = f"""
    You are a strategic Adtech/Martech advisor assessing an advertiser’s maturity based on their audit responses
    Provide a summary of each of the categories, using the column categories to group the data, 
    then using the answers and comments for all questions focusing on their current usage marketing maturity in their implementation for Adtech and Martech.
    Provide the response in a set of bullet points, these will be emailed and need to be understand by sales, marketing and adtech colleagues.
    
    Categories: {categories}
    Questions: {questions}
    Answers: {answers}
    Comments: {comments}
    """

    client = openai.OpenAI(api_key=st.secrets["OPEN_AI_KEY"])
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Imagine you are a marketing agency focused on Adtech and Martech and Google Marketing Platform."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )

    bullet_summary = response.choices[0].message.content
    return bullet_summary


def identify_top_maturity_gaps(df):
    
    subset = df.copy()

    questions = subset["Question"].tolist()
    answers = subset["Answer"].tolist()
    comments = subset["Comment"].fillna("").tolist() if "Comment" in df.columns else []

    prompt = f"""
You are a strategic Adtech/Martech advisor assessing an advertiser’s maturity based on their audit responses. 
Review the following questions, answers, and comments to identify the **most critical marketing maturity gaps**.
Focus the gaps on these three pillars
Identify and Eliminate Inefficiencies - Pinpoint overlaps, gaps and underutilized capabilities within your platforms, data and technology setup. This process uncovers opportunities to streamline your platform architecture, reduce wasted investment and unlock additional value from your inventory or first-party data assets.
Accelerate Innovation & Maturity - Expose maturity gaps that are holding back growth and highlight areas where new tools, approaches or AI-led solutions can be introduced. Ensure your organization stays up to speed with market shifts, embracing  cutting-edge practices, whilst building long-term competitive advantage.
Develop a Sustainable Growth Roadmap - Translate assessment insights into a prioritized, achievable plan, backed by identification of expertise & resources best positioned to deliver on the changes. This ensures that efficiency gains, capability enhancements and monetization opportunities are implemented effectively and sustained.
Each maturity gap should include:
- A concise **Heading** (e.g., "Lack of First-Party Data Activation")
- A brief 25 words or less **Context** (what the maturity driver is and why it matters)
- A clear 25 words or less **Impact** (how this gap is affecting the advertiser's performance or strategic outcomes)


Return a list of the gaps as structured objects like, ranked where #1 is the most impactful:
1. **Heading**: ...
   **Context**: ...
   **Impact**: ...

Questions: {questions}
Answers: {answers}
Comments: {comments}
"""

    client = openai.OpenAI(api_key=st.secrets["OPEN_AI_KEY"])
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a marketing maturity consultant focused on identifying key capability gaps from audits."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )

    maturity_gaps_text = response.choices[0].message.content

    # Parse the maturity gaps text into a list of dictionaries
    gaps = []
    gap_entries = re.split(r'\d+\.\s*\*\*Heading\*\*\:', maturity_gaps_text)

    for entry in gap_entries[1:]:
        heading_match = re.search(r'(.*?)\s*\*\*\s*Context\*\*\:', entry, re.DOTALL)
        context_match = re.search(r'\*\*\s*Context\*\*\:\s*(.*?)\s*\*\*\s*Impact\*\*\:', entry, re.DOTALL)
        impact_match = re.search(r'\*\*\s*Impact\*\*\:\s*(.*)', entry, re.DOTALL)

        heading = heading_match.group(1).strip() if heading_match else "N/A"
        context = context_match.group(1).strip() if context_match else "N/A"
        impact = impact_match.group(1).strip() if impact_match else "N/A"

        gaps.append({
            "Heading": heading,
            "Context": context,
            "Impact": impact
        })

    # Create a pandas DataFrame
    mat_gaps_df = pd.DataFrame(gaps)

    return mat_gaps_df

def identify_top_maturity_drivers(df):
    subset = df.copy()

    questions = subset["Question"].tolist()
    answers = subset["Answer"].tolist()
    comments = subset["Comment"].fillna("").tolist() if "Comment" in df.columns else []

    prompt = f"""
You are a strategic Adtech/Martech advisor assessing an advertiser’s maturity based on their audit responses. 
Review the following questions, answers, and comments to identify the **most critical marketing maturity drivers**.

A "maturity driver" is something that the business is currently doing well that accounts for their current level of marketing maturity, focused on their Google Marketing Platform usage.

Each maturity driver should include:
- A concise **Heading** (e.g., "Integration of First-Party Data")
- A brief 25 words or less **Context** (what the maturity driver is and why it matters)
- A clear 25 words or less **Impact** (how this driver improves the advertiser's maturity or strategic outcomes)

Return a list of the most critical drivers as structured objects like:
1. **Heading**: ...
   **Context**: ...
   **Impact**: ...

Questions: {questions}
Answers: {answers}
Comments: {comments}
"""

    client = openai.OpenAI(api_key=st.secrets["OPEN_AI_KEY"])
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a marketing maturity consultant focused on identifying key capability drivers from audits."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )

    maturity_drivers_text = response.choices[0].message.content

    # Parse the maturity gaps text into a list of dictionaries
    drivers = []
    drivers_entries = re.split(r'\d+\.\s*\*\*Heading\*\*\:', maturity_drivers_text)

    for entry in drivers_entries[1:]:
        heading_match = re.search(r'(.*?)\s*\*\*\s*Context\*\*\:', entry, re.DOTALL)
        context_match = re.search(r'\*\*\s*Context\*\*\:\s*(.*?)\s*\*\*\s*Impact\*\*\:', entry, re.DOTALL)
        impact_match = re.search(r'\*\*\s*Impact\*\*\:\s*(.*)', entry, re.DOTALL)

        heading = heading_match.group(1).strip() if heading_match else "N/A"
        context = context_match.group(1).strip() if context_match else "N/A"
        impact = impact_match.group(1).strip() if impact_match else "N/A"

        drivers.append({
            "Heading": heading,
            "Context": context,
            "Impact": impact
        })

    # Create a pandas DataFrame
    mat_drivers_df = pd.DataFrame(drivers)

    return mat_drivers_df

def create_full_report_pdf(summary, bullet_points, gaps_df, drivers_df, recommendations_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.set_font(style="B")
    pdf.cell(0, 10, "Category Summary", ln=True)
    pdf.set_font(style="")
    for line in summary.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf.set_font(style="B")
    pdf.cell(0, 10, "\nBullet Summary", ln=True)
    pdf.set_font(style="")
    for line in bullet_points.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf.set_font(style="B")
    pdf.cell(0, 10, "\nTop Maturity Gaps", ln=True)
    pdf.set_font(style="")
    for _, row in gaps_df.iterrows():
        pdf.multi_cell(0, 10, f"Heading: {row['Heading']}\nContext: {row['Context']}\nImpact: {row['Impact']}\n")

    pdf.set_font(style="B")
    pdf.cell(0, 10, "\nTop Maturity Drivers", ln=True)
    pdf.set_font(style="")
    for _, row in drivers_df.iterrows():
        pdf.multi_cell(0, 10, f"Heading: {row['Heading']}\nContext: {row['Context']}\nOpportunity: {row['Opportunity']}\n")

    pdf.set_font(style="B")
    pdf.cell(0, 10, "\nRecommendations", ln=True)
    pdf.set_font(style="")
    for _, row in recommendations_df.iterrows():
        pdf.multi_cell(0, 10, f"Recommendation: {row['Recommendation']}\nOverview: {row['Overview']}\nGMP Impact: {row['GMP Utilization Impact']}\nBusiness Impact: {row['Business Impact']}\n")

    return pdf.output(dest="S").encode("latin1")