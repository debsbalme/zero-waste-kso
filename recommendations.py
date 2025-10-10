import pandas as pd
import json
import math 
import openai
import streamlit as st
import ast

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

# Define the Recommendation Set as provided in your agent's internal knowledge base
RECOMMENDATION_SET = [
    {
        "question": "which automated bidding strategies have you used in dv360? please give further context of the performance in the comments section.",
        "answer": "Web analytics and funnel analysis",
        "type": "negative_choice",
        "recommendation": "Site Analytics Audit for Customer Experience",
        "overview": "We recommend conducting a Web Analytics Audit to ensure insights are being collected to identify the full breadth of friction points, drop-offs and gaps in user behavior tracking across your website. Accurate analytics enable data-led decisions to streamline user journeys, improve content relevance and reduce barriers to conversion. This leads to a more efficient customer experience, higher conversion rates and better ROI from existing traffic.",
        "gap": ""
    },
    {
        "question": "What types of data and modeling approaches does your organization currently use to inform and optimize scenario planning?",
        "answer": "Uplift or marginal return models to detect diminishing returns by channel or audience",
        "type": "negative_choice",
        "recommendation": "Data & AI Workshop (Incrementality Detection/Diminishin Return Modeling)",
        "overview": "We recommend exploring incrementality detection and diminishing return modeling to identify the true impact of media spend across channels and segments. By applying uplift modeling or marginal return curves, your organization can determine optimal investment levels, ensuring budget is allocated where it drives the most incremental value. This approach reduces waste, prevents over-investment in saturated areas, and improves overall media efficiency."
    },
    {
        "question": "What types of data and modeling approaches does your organization currently use to inform and optimize scenario planning?",
        "answer": "Time-series forecasting to account for seasonality and key calendar events",
        "type": "negative_choice",
        "recommendation": "Data & AI Workshop (Seasonal & Event-Based Forecasting)",
        "overview": "CWe recommend exploring seasonal and event-based forecasting using time-series models enhanced with anomaly detection. This approach helps anticipate fluctuations in demand, enabling more accurate planning around peak periods, holidays, and key commercial events. By aligning media and resource allocation with predicted performance shifts, your organization can reduce waste and maximize impact during critical windows."
    },
    {
        "question": "How does your organization currently identify and reduce spend on low-performing audience segments?",
        "answer": ["We review performance data manually and make adjustments periodically", "We rely on platform-level automation with limited manual oversight", "We do not currently evaluate or optimize audience segments based on performance", "Other"],
        "recommendation": "Data & AI Workshop (Wasted Impressions Mitigation)",
        "overview": "We recommend exploring the use of AI-driven audience performance modeling to mitigate wasted impressions by identifying and deprioritizing low-performing segments. Leveraging historical response data, behavioral signals, and third-party data can help train models that more precisely allocate spend toward high-value audiences. This approach enhances efficiency by reducing budget waste and improving overall campaign effectiveness."
    },
    {
        "question": "What methods does your organization currently use for marketing budget optimization? Select all those that apply.",
        "answer": ["Cross-channel budget planning tools or models (e.g. MMM, MTA, unified measurement)", "Scenario planning or forecasting tools to simulate future budget or future performance impact"],
        "type": "negative_choice",
        "recommendation": "Data & AI Workshop (AI Led Scenario Planning / Forecasting Tool to Simulate Future Performance of Marketing)",
        "overview": "We recommend exploring the implementation of an AI-led scenario planning and forecasting tool to simulate future performance across key areas of your marketing strategy. These tools leverage historical data and predictive models to forecast outcomes such as engagement, conversion, or revenue under different strategic approaches. This supports more informed decision-making, reduces reliance on trial-and-error, and improves overall marketing effectiveness through forward-looking insight."
    },
    {
        "question": "How does your organization currently identify and reduce spend on low-performing audience segments?",
        "answer": ["Data is generally consistent across key platforms with standard naming conventions and validation processes in place, but a few legacy or disconnected systems remain.", "Some key data sources are reliable but inconsistencies exist across platforms. Manual cleaning or reconciliation is often required", "Data is incomplete, inconsistent or siloed across systems. There is little to no confidence in data accuracy for decision making"],
        "recommendation": "Data & AI Workshop (Data Readiness Assessment)",
        "overview": "We recommend conducting a data readiness assessment to evaluate the quality, consistency, and structure of your data across sources. A strong, unified data foundation is critical for enabling high-efficiency use cases such as audience segmentation, personalization, measurement and AI-driven decisioning. Addressing gaps in data accuracy and alignment will unlock more reliable insights, reduce inefficiencies, and ensure your data strategy supports scalable, cross-functional marketing outcomes."
    },
    {
        "question": "What web analytics platform(s) do you have in place? Select all those that apply.",
        "match_criteria": {
            "min_matches": 2,
            "or_group": ["Adobe Analytics", "Google Analytics 4 (GA4)", "Google Analytics 360 (GA360)", "Heap Analytics", "HubSpot", "Matomo", "Mix Panel", "Other"]
        },
        "recommendation": "Platform Architecture Optimization Wedge (Web)",
        "overview": "Initial analysis suggests overlapping capabilities in web analytics platforms, with potential to streamline. We recommend conducting a thorough analysis of your current platform architecture to identify any overlapping capabilities, redundant technologies or critical gaps. This assessment will help streamline your martech stack, reduce unnecessary costs and ensure each platform plays a clear, complementary role. The outcome will drive greater operational efficiency, improve data integration and enable a more scalable, future-ready marketing infrastructure."
    },
    {
        "question": "Do you have a data warehouse in place? If so please specify those that apply.",
        "match_criteria": {
            "min_matches": 2,
            "or_group": ["Amazon Redshift", "Google BigQuery", "Microsoft Azure Synapse Analytics", "Snowflake", "Other"]
        },
        "recommendation": "Platform Architecture Optimization Wedge (DW)",
        "overview": "Initial analysis suggests overlapping capabilities in data warehouse platforms, with potential to streamline. We recommend conducting a thorough analysis of your current platform architecture to identify any overlapping capabilities, redundant technologies or critical gaps. This assessment will help streamline your martech stack, reduce unnecessary costs and ensure each platform plays a clear, complementary role. The outcome will drive greater operational efficiency, improve data integration and enable a more scalable, future-ready marketing infrastructure."
    },
    {
        "question": "Do you have any Data Cleanrooms in place? If so please specify which data cleanroom(s) apply.",
        "match_criteria": {
            "min_matches": 2,
            "or_group": ["Amazon Marketing Cloud (AMC)", "Google Ads Data Hub (ADH)", "InfoSum", "LiveRamp", "Snowflake", "Other"]
        },
        "recommendation": "Platform Architecture Optimization Wedge (Clean)",
        "overview": "Initial analysis suggests overlapping capabilities in data cleanrooms, with potential to streamline. We recommend conducting a thorough analysis of your current platform architecture to identify any overlapping capabilities, redundant technologies or critical gaps. This assessment will help streamline your martech stack, reduce unnecessary costs and ensure each platform plays a clear, complementary role. The outcome will drive greater operational efficiency, improve data integration and enable a more scalable, future-ready marketing infrastructure."
    },
    {
        "question": "How would you describe your organization’s current approach to evaluating and optimizing your marketing technology stack?",
        "answer": ["We’ve identified some redundancy or inefficiencies in our platform setup but have not prioritized a full in-depth review due to lack of resources.", "We suspect or are aware of overlapping capabilities across platforms but have not prioritized addressing them due to lack of resources.", "We do not have the resources or processes in place to assess or optimize our platform architecture. Any overlaps or inefficiencies are currently unaddressed."],
        "recommendation": "Platform Architecture Optimization Wedge (Arch)",
        "overview": "We recommend conducting a thorough analysis of your current platform architecture to identify any overlapping capabilities, redundant technologies or critical gaps. This assessment will help streamline your martech stack, reduce unnecessary costs and ensure each platform plays a clear, complementary role. The outcome will drive greater operational efficiency, improve data integration and enable a more scalable, future-ready marketing infrastructure."
    },
    {
        "set_id": "SAA1Pa",
        "questions": [
            {
                "question": "What initiatives does your organization currently have in place to drive greater efficiency in audience strategy and activation?",
                "answer": ["Website and app behavioral data", "We do not currently build first party audiences"],
                "type": "negative_choice"
            },
            {
                "question": "What web analytics platform(s) do you have in place? Select all those that apply.",
                "answer": "n/a",
                "type": "negative_choice"
            }
        ],
        "recommendation": "Site Analytics Audit for 1P Audience Builds",
        "overview": "We recommend conducting a Web Analytics Audit to ensure accurate and complete data collection for building high-quality first-party audiences. Clean, structured data improves targeting, reduces media waste and enables more effective personalization. This foundational step enhances audience strategy and drives greater marketing efficiency across channels."
    },
    {
        "set_id": "SAA1Pb",
        "questions": [
            {
                "question": "What data sources are utilized to build out first party audiences?",
                "answer": "Use of first-party data to build custom audience segments"
            },
            {
                "question": "What web analytics platform(s) do you have in place? Select all those that apply.",
                "answer": "n/a",
                "type": "negative_choice"
            },
            {
                "question": "Select all of the following that match the user insights your organization gains from website or app data?",
                "answer": ["We use website/app data to predict user behavior and personalize experiences.", "We use website data to model out customer lifetime value.", "We tie website/app actions to objectives and key results (OKRs)"],
                "type": "negative_choice"
            }
        ],
        "recommendation": "Site Analytics Audit for 1P Audience Builds",
        "overview": "We recommend conducting a Web Analytics Audit to ensure accurate and complete data collection for building high-quality first-party audiences. Clean, structured data improves targeting, reduces media waste and enables more effective personalization. This foundational step enhances audience strategy and drives greater marketing efficiency across channels."
    },
    {
        "set_id": "SAACexp",
        "questions": [
            {
                "question": "What methods of analysis does your organization use to optimize and improve customer experience on your website or app.",
                "answer": "Web analytics and funnel analysis"
            },
            {
                "question": "What web analytics platform(s) do you have in place? Select all those that apply.",
                "answer": "n/a",
                "type": "negative_choice"
            },
            {
                "question": "Select all of the following that match the user insights your organization gains from website or app data?",
                "answer": ["We are able to identify user journey drop-off points and optimize conversion paths.", "We use website/app data to predict user behavior and personalize experiences."],
                "type": "negative_choice"
            }
        ],
        "recommendation": "Site Analytics Audit for Customer Experience",
        "overview": "We recommend conducting a Web Analytics Audit to ensure insights are being collected to identify the full breadth of friction points, drop-offs and gaps in user behavior tracking across your website. Accurate analytics enable data-led decisions to streamline user journeys, improve content relevance and reduce barriers to conversion. This leads to a more efficient customer experience, higher conversion rates and better ROI from existing traffic."
    },
    {
        "set_id": "HM_Cexp",
        "questions": [
            {
                "question": "What methods of analysis does your organization use to optimize and improve customer experience on your website or app.",
                "answer": "Heatmapping",
                "type": "negative_choice"
            },
            {
                "question": "Select all of the following that match the user insights your organization gains from website or app data?",
                "answer": [
                    "We track which pages or products users are most engaged with.",
                    "We are able to identify user journey drop-off points and optimize conversion paths."
                ],
                "type": "negative_choice"
            }
        ],
        "recommendation": "Heatmapping for Customer Experience Insights & Improvements",
        "overview": "We recommend exploring heatmapping tools to gain visual insights into user behavior across key website or app pages. Heatmaps highlight where users click, scroll and drop off, enabling teams to identify friction points, content blind spots, and usability issues. This helps prioritize experience improvements that reduce abandonment and drive greater efficiency in conversion performance."
    },
    {
        "set_id": "propensity",
        "questions": [
            {
                "question": "What initiatives does your organization currently have in place to drive greater efficiency in audience strategy and activation?",
                "answer": "Predictive modeling or AI to identify high-value users or churn risk",
                "type": "negative_choice"
            },
            {
                "question": "Select all of the following that match the user insights your organization gains from website or app data?",
                "answer": "We use website data to model out customer lifetime value."
            }
        ],
        "recommendation": "Propensity Modelling",
        "overview": "We recommend implementing propensity modelling powered by web analytics data to better understand user intent and likelihood to convert. This approach uses on-site behavioral signals to identify high-potential audiences for more targeted activation. It enables more efficient use of marketing spend by prioritizing users with greater likelihood to take action."
    },
    {
        "set_id": "adv_prop_crm",
        "questions": [
            {
                "question": "Select all of the following that match the user insights your organization gains from website or app data?",
                "answer": "We use website data to model out customer lifetime value."
            },
            {
                "question": "What initiatives does your organization currently have in place to drive greater efficiency in audience strategy and activation?",
                "answer": "Predictive modeling or AI to identify high-value users or churn risk"
            },
            {
                "question": "What data are you utilizing to model out customer lifetime value or likelihood?",
                "answer": "CRM Data",
                "type": "negative_choice"
            },
            {
                "question": "what are your media campaign goals?",
                "answer": [
                    "$500K – $1M",
                    "$1M – $5M",
                    "$5M – $10M",
                    "More than $10M"
                ]
            }
        ],
        "recommendation": "Advanced propensity modelling to tie into business impacts (website data + CRM data)",
        "overview": "We recommend incorporating CRM data into propensity modelling to align predictions with key business goals such as retention, upsell, or reactivation. This integration enriches the models with customer history and lifecycle signals, enabling more precise targeting. It supports greater marketing efficiency by ensuring efforts are focused on driving measurable business outcomes."
    },
    {
        "set_id": "adv_prop_3rd",
        "questions": [
            {
                "question": "Select all of the following that match the user insights your organization gains from website or app data?",
                "answer": "We use website data to model out customer lifetime value."
            },
            {
                "question": "What initiatives does your organization currently have in place to drive greater efficiency in audience strategy and activation?",
                "answer": "Predictive modeling or AI to identify high-value users or churn risk"
            },
            {
                "question": "What data are you utilizing to model out customer lifetime value or likelihood?",
                "answer": "Third Party Licensed Data",
                "type": "negative_choice"
            },
            {
                "question": "what are your media campaign goals?",
                "answer": [
                    "$500K – $1M",
                    "$1M – $5M",
                    "$5M – $10M",
                    "More than $10M"
                ]
            }
        ],
        "recommendation": "Advanced propensity modelling to enhanced third party licensed data for additional lift in modelling",
        "overview": "We recommend exploring the use of licensed third-party data to enrich propensity models and improve accuracy. Supplementing internal data with broader behavioral, demographic, or lifestyle signals helps fill gaps, refine targeting, and expand reach to lookalike audiences, improving model precision and enabling more efficient audience activation at scale."
    },
    {
        "set_id": "CP_Audiences",
        "questions": [
            {
                "and_group_name": "Group 1: Q1 or Q2",
                "or_group": [
                    {
                        "question": "What DSP(s), Demand-Side Platforms, do you currently have in place?",
                        "answer": "Google Display & Video 360 (DV360)"
                    },
                    {
                        "question": "What Paid Search platform(s) do you currently have in place?",
                        "answer": ["Google Ads", "Google Search Ads 360 (SA360)"]
                    }
                ]
            },
            {
                "and_group_name": "Group 2: Q3 must be true",
                "or_group": [
                    {
                        "question": "What web analytics platform(s) do you have in place? Select all those that apply.",
                        "answer": ["Google Analytics 4 (GA4)", "Google Analytics 360 (GA360)"]
                    }
                ]
            },
            {
                "and_group_name": "Group 2: Q3 must be true",
                "or_group": [
                    {
                        "question": "Do you have a data warehouse in place? If so please specify those that apply.",
                        "answer": "Google BigQuery"
                    }
                ]
            }
        ],
        "recommendation": "Cloud Patterns For Audiences",
        "overview": "We recommend reconfiguring your use of Google Analytics, BigQuery, and the broader Google Marketing Platform (GMP) to function as a scalable, flexible alternative to a Customer Data Platform (CDP). By integrating and centralizing your customer data within this ecosystem, you can unify audiences, enable advanced segmentation, and activate personalized campaigns across channels more efficiently. This approach maximizes existing investments, improves data accessibility, and supports real-time insights for smarter marketing decisions."
    },
    {
        "set_id": "CleanConsult",
        "questions": [
            {
                "question": "Do you have any Data Cleanrooms in place? If so please specify which data cleanroom(s) apply.",
                "answer": "n/a"
            },
            {
                "question": "Which of the following data usage activities does your organization currently engage in?",
                "answer": "n/a",
                "type": "negative_choice"
            }
        ],
        "recommendation": "Cleanroom Consultation",
        "overview": " We recommend exploring data cleanrooms to enable secure audience matching, insights generation, and campaign measurement in collaboration with media partners. Cleanrooms allow for privacy-safe data integration, improving match rates and enabling deeper analysis of performance across platforms without exposing raw user data. This drives efficiency by enhancing targeting accuracy, reducing duplication and delivering more informed media investments."
    },
    {
        "set_id": "DataAI_ASO",
        "questions": [
            {
                "question": "What types of data and modeling approaches does your organization currently use to inform and optimize scenario planning?",
                "answer": "Platform-native AI bidding tools (e.g. Google Smart Bidding, Meta Advantage+)"
            },
            {
                # This question object was missing the "question" key, causing the KeyError
                "question": "What types of data and modeling approaches does your organization currently use to inform and optimize scenario planning?",
                "answer": "Custom auction strategies using third-party API integrations",
                "type": "negative_choice"
            }
        ],
        "recommendation": "Data & AI Workshop (Auction Strategy Optimization)",
        "overview": "We recommend assessing your current auction strategies to compare the effectiveness of native AI-based bid tools (e.g. Google Smart Bidding, Meta Advantage+) with custom bidding strategies powered by third-party APIs. This evaluation can uncover opportunities to improve cost-efficiency, enhance control and better align bidding logic with your unique performance goals. Optimizing auction strategy ensures smarter spend and improved return across key platforms."
    },
    {
        "set_id": "DataAI_AORF",
        "questions": [
            {
                "and_group_name": "Group 1: Q1 or Q2",
                "or_group": [
                    {
                        "question": "How does your organization currently manage audience overlap across campaigns or platforms?",
                        "answer": ["We conduct audience overlap checks using platform-native tools", "We are aware of potential overlap but do not actively manage it", "Other"]
                    },
                    {
                        "question": "What methods does your organization use to control reach and frequency across campaigns?",
                        "answer": ["Cross-platform frequency management", "Frequency logic based on user behavior or engagement decay", "In-platform frequency capping (e.g. within Meta, Google)"],
                        "type": "negative_choice"
                    }
                ]
            },
            {
                "and_group_name": "Group 2: Q3 must be true",
                "or_group": [
                    {
                        "question": "What initiatives does your organization currently have in place to drive greater efficiency in audience strategy and activation?",
                        "answer": ["Regular analysis of audience overlap and performance impact", "Audience suppression to reduce duplication and avoid wasted spend", "Application of reach and frequency capping to reduce overspend and improve exposure efficiency"]
                    }
                ]
            }
        ],
        "recommendation": "Data & AI Workshop (Audience Overlap Reduction & Frequency Control)",
        "overview": "We recommend implementing AI and machine learning models to analyze audience overlap across campaigns and platforms, enabling the suppression of redundant reach. Incorporating frequency capping logic tied to predicted decay in incremental lift helps optimize exposure, preventing audience fatigue and improving engagement. This strategy increases marketing efficiency by maximizing the value of each impression and reducing wasted spend."
    },
    {
        "set_id": "DataAI_WIM",
        "questions": [
            {
                "question": "How does your organization currently identify and reduce spend on low-performing audience segments?",
                "answer": ["We use AI or machine learning models to assess segment performance and adjust spend dynamically", "We review performance data manually and make adjustments periodically"]
            },
            {
                "question": "What types of data inform your audience performance evaluation?",
                "answer": ["Historical campaign response or conversion data", "On-site or in-app behavioral data (e.g. bounce rate, session depth)", "Third-party or licensed audience data", "Predictive analytics or modeling tools"],
                "type": "negative_choice"
            }
        ],
        "recommendation": "Data & AI Workshop (Wasted Impressions Mitigation)",
        "overview": "We recommend enhancing the the use of AI-driven audience performance modeling to mitigate wasted impressions by leveraging additional data sources tp train models that more precisely allocate spend toward high-value audiences. This approach enhances efficiency by reducing budget waste and improving overall campaign effectiveness."
    },
    {
        "set_id": "DataAI_LAL",
        "questions": [
            {
                "question": "What initiatives does your organization currently have in place to drive greater efficiency in audience strategy and activation?",
                "answer": "Lookalike or similarity modeling for prospecting"
            },
            {
                "question": "How does your organization currently build and optimize lookalike or similar audience segments for prospecting?",
                "answer": "We use our own AI-based clustering and advanced data modeling to create lookalike audiences",
                "type": "negative_choice"
            }
        ],
        "recommendation": "Data & AI Workshop (Lookalike improvement & cost effective segment targeting)",
        "overview": "We recommend evolving beyond rule-based lookalike models by adopting AI-driven clustering to identify high-potential prospect segments. This approach increases precision by grouping users based on deeper behavioral and demographic patterns, rather than basic similarity rules. As a result, it improves conversion rates, reduces customer acquisition costs (CAC), and drives greater efficiency across prospecting campaigns."
    },
    {
        "set_id": "DataAI_DSO",
        "questions": [
            {
                "question": "What initiatives does your organization currently have in place to drive greater efficiency in audience strategy and activation?",
                "answer": "Audience suppression to reduce duplication and avoid wasted spend"
            },
            {
                "question": "How does your organization currently manage audience suppression to avoid overexposure?",
                "answer": ["We use real-time data and AI-driven rules to dynamically suppress users based on exposure recency, engagement or lifecycle status", "We apply suppression lists that are updated in real time based on user actions"],
                "type": "negative_choice"
            }
        ],
        "recommendation": "Data & AI Workshop (Dynamic Suppression Optimization",
        "overview": "We recommend exploring dynamic suppression optimization to improve audience efficiency and reduce wasted impressions. By leveraging real-time data, such as recent ad exposure, engagement signals, or customer lifecycle stage, your organization can suppress users who are unlikely to convert or have recently re-engaged. This approach minimizes oversaturation, improves user experience, and reallocates budget toward higher-performing segments, ultimately driving stronger campaign performance."
    },
    {
        "set_id": "RMN_DEEM",
        "questions": [
            {
                "question": "Does your organization currently monetize its first party data?",
                "answer": ["Selling or licensing data to external partners", "Offering audience targeting across owned inventory to brand partners", "First party data matching (e.g. through clean rooms) for activations", "First party data matching (e.g. through clean rooms) for insights or measurement"]
            },
            {
                "question": "How does your organization enhance first-party audience data to support monetization strategies?",
                "answer": ["We occasionally use external data to supplement first-party audiences for monetization purposes", "We currently rely solely on raw first-party data for audience monetization but are exploring enrichment options", "We do not enrich first-party audiences for monetization"]
            }
        ],
        "recommendation": "RMN/Commerce Workshop (Data Enrichment for Enhanced Monetization)",
        "overview": "We recommend leveraging additional data sets for data enrichment to enhance your first-party data profiles, unlocking deeper audience insights and more precise targeting. By integrating additional demographic, behavioral, or contextual data, you can increase the value and relevance of your data assets for partners and advertisers. This enrichment supports more effective monetization strategies, driving higher engagement and improved ROI across your marketing and retail media efforts."
    },
    {
        "set_id": "RMN_InHouse",
        "questions": [
            {
                "question": "Does your organization have any of the following owned and operated channels?",
                "answer": "n/a",
                "type": "negative_choice"
            },
            {
                "question": "Does your organization currently monetize its first party data?",
                "answer": ["Selling or licensing data to external partners", "Offering audience targeting across owned inventory to brand partners", "First party data matching (e.g. through clean rooms) for activations", "First party data matching (e.g. through clean rooms) for insights or measurement"]
            },
            {
                "question": "Who currently manages the monetization of your owned and operated channels and/or data?",
                "answer": ["Managed by an external agency or consultancy", "Managed collaboratively by in-house teams and external agency or consultancy", "Currently no clear ownership of owned & operated channel/data monetization"]
            }
        ],
        "recommendation": "RMN/Commerce Workshop (In-House Monetization)",
        "overview": "We recommend consolidating owned and operated channel monetization in-house to gain greater control, transparency, and profitability. By building a dedicated team or establishing clear internal ownership, your organization can directly manage media partner relationships, audience activation, and revenue streams. This approach improves operational efficiency, aligns monetization efforts with broader business goals, and captures a larger share of revenue by reducing external fees."
    },
    {
        "set_id": "CRoom_SS",
        "questions": [
            {
                "question": "How would you describe your organization’s current approach to evaluating and optimizing your marketing technology stack?",
                 "match_criteria": {
                 "min_matches": 4,
              "or_group": ["Audience activation","Audience overlap analysis","Data collaboration with media partners","Incrementality or lift analysis","Measurement and attribution","Reach and frequency insights"]
             },
            "type": "negative_choice"
            },
            {
                "question": "Are your data cleanroom(s) currently integrated with any external media, data or technology partners?",
                "answer": "Yes, we collaborate with majority of key partners partners via cleanrooms",
                "type": "negative_choice"
            },
            {
                "question": "Do you have any Data Cleanrooms in place? If so please specify which data cleanroom(s) apply.",
                "answer": ["Amazon Marketing Cloud (AMC)","Google Ads Data Hub (ADH)","InfoSum","LiveRamp","Snowflake","Other"]
            }
        ],
        "recommendation": "Cleanroom Stewardship",
        "overview": "We recommend maximizing the value of your existing data cleanroom by expanding both the number of integrated partners (e.g. media, retail and tech platforms) and the range of use cases. This broader usage drives marketing efficiency by enabling smarter investments, reducing duplication and delivering a more unified, data-driven strategy across channels."
    },
    {
        "set_id": "RMN_CommStrat",
        "questions": [
            {
                "question": "Does your organization currently monetize its first party data?",
                "answer": "We do not currently monetize our first-party data"
            },
            {
                "question": "Which of the following challenges does your organization currently face when it comes to monetizing first-party data or owned and operated channels?",
                "answer": ["Lack of a defined monetization strategy or business case","Limited visibility into the performance or value of owned channels","Fragmented data or absence of a unified audience view","Limited internal expertise or resources to support monetization"]
            }
        ],
        "recommendation": "RMN/Commerce Workshop (RMN & Commerce Strategy Development)",
        "overview": "We recommend exploring the opportunity to develop a retail media network and commerce strategy focused on monetizing your first-party data and/or owned & operated channels. Begin with an audit of your existing channels and data assets to assess their readiness and identify your unique “right to win” value proposition. This will help uncover revenue opportunities, optimize audience activation, and create a sustainable, differentiated commerce ecosystem that drives incremental growth."
    },
    {
        "set_id": "RMN_InHouse",
        "questions": [
            {
                "question": "Does your organization have any of the following owned and operated channels?",
                "answer": ["E-commerce website or app","Physical retail locations","Email or SMS marketing lists","Loyalty or rewards program","Mobile app with logged-in users","On-site product listings","Owned social media channels","Connected TV or OTT app","Self-service portal or account area","Other"]
            },
            {
                "question": "Who currently manages the monetization of your owned and operated channels and/or data?",
                "answer": ["Managed by an external agency or consultancy","Managed collaboratively by in-house teams and external agency or consultancy","Currently no clear ownership of owned & operated channel/data monetization"]
            },
            {
                "question": "Does your organization currently monetize its first party data?",
                "answer": ["Selling or licensing data to external partners","Offering audience targeting across owned inventory to brand partners","First party data matching (e.g. through clean rooms) for activations","First party data matching (e.g. through clean rooms) for insights or measurement"]
            }
        ],
        "recommendation": "RMN/Commerce Workshop (In-House Management)",
        "overview": "Consider building in-house capabilities to manage your retail media network strategy. This approach can drive greater efficiency by enabling tighter integration of data, faster decision-making, and more control over monetization levers. It also reduces reliance on third parties, allowing for more agile testing, optimization and alignment with broader business goals."
    },
    {
        "set_id": "plat_af_web",
        "match_answers_from_questions": [
            "What web analytics platform(s) do you have in place? Select all those that apply.",
            "Do you have an app analytics platform?"
        ],
        "recommendation": "Platform Architecture Optimization Wedge (Web+App)",
        "overview": "Initial analysis suggests overlapping capabilities in web and app analytics platforms, with potential to streamline. We recommend conducting a thorough analysis of your current platform architecture to identify any overlapping capabilities, redundant technologies or critical gaps. This assessment will help streamline your martech stack, reduce unnecessary costs and ensure each platform plays a clear, complementary role. The outcome will drive greater operational efficiency, improve data integration and enable a more scalable, future-ready marketing infrastructure."
    }
]


_DEFAULT_THEME_MAP: Dict[str, Iterable[str]] = {
# Architecture & Platforms
"Platform Architecture Optimization": [
"architecture", "platform", "stack", "redundant", "overlap", "streamline", "optimization wedge",
"web analytics", "app analytics", "data warehouse", "bigquery", "redshift", "snowflake", "synapse",
],
# Data & AI modelling / forecasting
"Data & AI Modelling & Forecasting": [
"model", "modelling", "modeling", "uplift", "propensity", "forecast", "time-series", "diminishing",
"incrementality", "auction", "optimization", "scenario", "predict", "clv",
],
# Audiences (build, lookalike, suppression, overlap)
"Audience Strategy & Activation": [
"audience", "lookalike", "similarity", "suppression", "overlap", "segment", "activation", "prospecting",
"high-value", "reach", "frequency", "wasted impressions",
],
# Analytics & CX
"Analytics & Customer Experience": [
"analytics", "heatmap", "heatmapping", "funnel", "journey", "conversion path", "cx", "experience",
"web analytics audit", "site analytics",
],
# Cleanrooms & data collaboration
"Data Cleanrooms & Collaboration": [
"cleanroom", "clean room", "ads data hub", "adh", "amazon marketing cloud", "amc", "infosum", "liveramp",
"collaboration", "match rate",
],
# Retail media & monetization
"Retail Media & Monetization": [
"retail media", "rmn", "monetization", "in-house", "owned and operated", "o&o", "commerce",
"data enrichment", "partner",
],
}


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

    # NOTE: The RECOMMENDATION_SET is assumed to be a global or imported list
    # of dictionaries defining the recommendation logic.
    if 'RECOMMENDATION_SET' not in globals():
        print("Error: RECOMMENDATION_SET is not defined.")
        return {
            'matched_recommendations': [],
            'total_matched_recommendations': 0,
            'total_score': 0.0,
            'total_max_score': 0.0
        }

    for item in RECOMMENDATION_SET:
        if "set_id" not in item:
            # A. Single Question Recommendation
            if 'question' not in item or 'answer' not in item:
                print(f"Skipping recommendation item due to missing 'question' or 'answer' key: {item}")
                continue

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
            group_recommendation = item['recommendation']
            rec_overview = item.get('overview', 'N/A')
            rec_gmp_impact = item.get('gmpimpact', 'N/A')
            rec_business_impact = item.get('businessimpact', 'N/A')

            group_condition_met = False
            current_group_contributing_scores = 0.0
            current_group_contributing_max_weights = 0.0

            # --- Logic for 'match_answers_from_questions' ---
            if 'match_answers_from_questions' in item and len(item['match_answers_from_questions']) == 2:
                q1_key = item['match_answers_from_questions'][0].lower().strip()
                q2_key = item['match_answers_from_questions'][1].lower().strip()

                q1_entry = csv_data_map.get(q1_key)
                q2_entry = csv_data_map.get(q2_key)

                # Check if both questions exist in the CSV data and their normalized answers are the same.
                if q1_entry and q2_entry:
                    q1_answers = q1_entry['answers']
                    q2_answers = q2_entry['answers']

                    if q1_answers and q2_answers and q1_answers[0] == q2_answers[0] and q1_answers[0] != "":
                        group_condition_met = True
                        current_group_contributing_scores = q1_entry.get('score', 0.0) + q2_entry.get('score', 0.0)
                        current_group_contributing_max_weights = q1_entry.get('maxweight', 0.0) + q2_entry.get('maxweight', 0.0)

            # --- Logic for 'min_matches', 'or_group', and 'AND' ---
            else:
                group_questions = item['questions']
                contributing_matches = []
                for sub_q_item in group_questions:
                    # Check if 'question' and 'answer' keys exist in the sub-question item
                    if 'question' not in sub_q_item or 'answer' not in sub_q_item:
                        print(f"Skipping sub-question item due to missing 'question' or 'answer' key: {sub_q_item}")
                        continue

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

                    # If the sub-question condition IS met, add its score and maxweight
                    if current_sub_q_condition_met and csv_sub_q_entry:
                        contributing_matches.append({
                            'score': csv_sub_q_entry.get('score', 0.0),
                            'maxweight': csv_sub_q_entry.get('maxweight', 0.0)
                        })

                min_matches_required = item.get('min_matches')
                is_or_group = item.get('or_group')

                if min_matches_required is not None:
                    # Check if the number of contributing matches meets the minimum
                    group_condition_met = len(contributing_matches) >= min_matches_required
                elif is_or_group:
                    # Check if at least one sub-question matched
                    group_condition_met = len(contributing_matches) > 0
                else:
                    # Default to the original 'AND' logic: all sub-questions must match
                    group_condition_met = len(contributing_matches) == len(group_questions)

                if group_condition_met:
                    current_group_contributing_scores = sum(m['score'] for m in contributing_matches)
                    current_group_contributing_max_weights = sum(m['maxweight'] for m in contributing_matches)

            # If the group's overall condition is met, add the group recommendation
            if group_condition_met:
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
    Provide the response in the form of a written paragraph each less than 500 words.
    Please provide the summary for each of the categories provided.
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
        max_tokens=2000,
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


def identify_top_maturity_gaps(df, model_name: str = "gpt-4.1-mini", max_tokens: int = 1200) -> pd.DataFrame:
    """
    Generate maturity gaps PER CATEGORY using the 'Category' column.
    Returns a DataFrame with columns: Category, Heading, Context, Impact.

    Notes:
      - Loops each category separately to keep outputs well-scoped.
      - Robust parsing for numbered gaps in the format:
          1. **Heading**: ...
             **Context**: ...
             **Impact**: ...
      - Skips empty/missing categories gracefully.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["Category", "Heading", "Context", "Impact"])

    # Ensure required columns exist
    for col in ["Category", "Question", "Answer"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    # Safe comments field
    has_comments = "Comment" in df.columns

    all_rows = []

    # Iterate categories (string-cast to avoid nan weirdness)
    categories = (
        df["Category"]
        .apply(lambda x: "" if pd.isna(x) else str(x))
        .unique()
        .tolist()
    )

    # Remove empty category labels if any
    categories = [c for c in categories if c.strip() != ""]

    if not categories:
        return pd.DataFrame(columns=["Category", "Heading", "Context", "Impact"])

    client = openai.OpenAI(api_key=st.secrets["OPEN_AI_KEY"])

    for cat in categories:
        sub = df[df["Category"].astype(str) == cat].copy()
        if sub.empty:
            continue

        questions = sub["Question"].fillna("").astype(str).tolist()
        answers = sub["Answer"].fillna("").astype(str).tolist()
        comments = sub["Comment"].fillna("").astype(str).tolist() if has_comments else []

        prompt = f"""
You are a strategic Adtech/Martech advisor assessing an advertiser’s maturity based on their audit responses.

Focus ONLY on the Category: "{cat}".

From the questions, answers, and (if provided) comments below, identify the most critical **marketing maturity gaps** for this category.

Anchor your thinking to these three pillars:
1) Identify & Eliminate Inefficiencies — overlaps, gaps, and underutilized capabilities across platforms, data, and tech; streamline architecture; reduce wasted investment.
2) Accelerate Innovation & Maturity — expose gaps blocking growth; introduce new tools, approaches, or AI-led solutions to keep pace with market shifts.
3) Develop a Sustainable Growth Roadmap — translate insights into a prioritized, achievable plan with resourcing, so gains are implemented and sustained.

For each gap, return:
- **Heading**: concise title (e.g., "Lack of First-Party Data Activation")
- **Context**: ≤25 words describing the gap
- **Impact**: ≤25 words on impact to platform architecture, data quality, audience strategy, technology use, marketing strategy, or business outcomes

Output strictly as a numbered list:
1. **Heading**: ...
   **Context**: ...
   **Impact**: ...

Questions: {questions}
Answers: {answers}
Comments: {comments}
        """.strip()

        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a marketing maturity consultant focused on identifying key capability gaps from audits."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.6,
        )

        text = resp.choices[0].message.content if resp and resp.choices else ""

        # --- Parse the maturity gaps text into rows for this category ---
        gaps = []
        # split on "1. **Heading**:" / "2. **Heading**:" etc
        parts = re.split(r'\n?\s*\d+\.\s*\*\*Heading\*\*\s*:\s*', text)
        # First split element is preamble; skip it
        for chunk in parts[1:]:
            # heading is the text up to **Context**:
            heading_match = re.match(r'(.*?)\s*\*\*\s*Context\*\*\s*:\s*(.*)', chunk, re.DOTALL)
            if heading_match:
                heading_text = heading_match.group(1).strip()
                rest = heading_match.group(2)
            else:
                # fallback: try to parse up to a newline
                first_line = chunk.strip().splitlines()[0] if chunk.strip() else "N/A"
                heading_text = first_line.strip()
                rest = chunk[len(first_line):]

            context_match = re.search(r'\*\*\s*Context\*\*\s*:\s*(.*?)\s*\*\*\s*Impact\*\*\s*:\s*(.*)', rest, re.DOTALL)
            if context_match:
                context_text = context_match.group(1).strip()
                impact_text = context_match.group(2).strip()
            else:
                # Fallback: try to grab lines labeled Context/Impact even if formatting drifts
                context_alt = re.search(r'Context\s*:\s*(.*)', rest)
                impact_alt = re.search(r'Impact\s*:\s*(.*)', rest)
                context_text = context_alt.group(1).strip() if context_alt else "N/A"
                impact_text = impact_alt.group(1).strip() if impact_alt else "N/A"

            gaps.append({
                "Category": cat,
                "Heading": heading_text or "N/A",
                "Context": context_text or "N/A",
                "Impact": impact_text or "N/A",
            })

        all_rows.extend(gaps)

    mat_gaps_df = pd.DataFrame(all_rows, columns=["Category", "Heading", "Context", "Impact"])

    # Drop empty rows if any
    if not mat_gaps_df.empty:
        mat_gaps_df = mat_gaps_df[
            ~(
                mat_gaps_df[["Heading", "Context", "Impact"]]
                .replace("N/A", "")
                .apply(lambda r: all(x.strip() == "" for x in r), axis=1)
            )
        ].reset_index(drop=True)

    return mat_gaps_df
 


def identify_top_maturity_drivers(df):
    subset = df.copy()

    questions = subset["Question"].tolist()
    answers = subset["Answer"].tolist()
    comments = subset["Comment"].fillna("").tolist() if "Comment" in df.columns else []

    prompt = f"""
You are a strategic Adtech/Martech advisor assessing an advertiser’s maturity based on their audit responses. 
Review the following questions, answers, and comments to identify the **most critical marketing maturity drivers**.

Focusing on these three pillars
Identify and Eliminate Inefficiencies - Pinpoint overlaps, gaps and underutilized capabilities within your platforms, data and technology setup. This process uncovers opportunities to streamline your platform architecture, reduce wasted investment and unlock additional value from your inventory or first-party data assets.
Accelerate Innovation & Maturity - Expose maturity gaps that are holding back growth and highlight areas where new tools, approaches or AI-led solutions can be introduced. Ensure your organization stays up to speed with market shifts, embracing  cutting-edge practices, whilst building long-term competitive advantage.
Develop a Sustainable Growth Roadmap - Translate assessment insights into a prioritized, achievable plan, backed by identification of expertise & resources best positioned to deliver on the changes. This ensures that efficiency gains, capability enhancements and monetization opportunities are implemented effectively and sustained.

A "maturity driver" is something that the business is currently doing well that accounts for their current level of marketing maturity, focused on their Google Marketing Platform usage.
For each Category, Review the questions, answers, and comments to identify the **most critical marketing maturity drivers**.

Each maturity driver should include:
- A concise **Heading** (e.g., "Integration of First-Party Data")
- A brief 25 words or less **Context** (what the maturity driver is and why it matters)
- A clear 25 words or less **Impact** (how this driver improves the advertiser's maturity or strategic outcomes)

For each category, Return the Category as a Header, and then return a list of the gaps as structured objects like, ranked where #1 is the most impactful:
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



def _normalize_text(s: Optional[str]) -> str:
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    return re.sub(r"\s+", " ", str(s).lower()).strip()


def _best_theme(text: str, theme_map: Dict[str, Iterable[str]]) -> Tuple[str, int]:
    """Return (theme, score) with highest keyword hits; 'Other' if none."""
    best_theme, best_score = "Other", 0
    for theme, keywords in theme_map.items():
        score = 0
        for kw in keywords:
            # word boundary for single tokens; simple contains for phrases
            if " " in kw:
                score += text.count(kw)
            else:
                score += len(re.findall(rf"\b{re.escape(kw)}\b", text))
        if score > best_score:
            best_theme, best_score = theme, score
    return (best_theme if best_score > 0 else "Other", best_score)




def process_and_summarize_recommendations(
    recommendations_df: pd.DataFrame,
    theme_map: Optional[Dict[str, Iterable[str]]] = None,
    top_k: int = 6,
    include_examples: bool = True,
    example_limit: int = 3,
    openai_api_key: str = "YOUR_API_KEY" # Replace with your actual key or use secrets management
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Groups recommendations by theme, gets summaries from ChatGPT, and returns
    the themes DataFrame and a dictionary of theme summaries.

    Args:
        recommendations_df: DataFrame containing recommendations.
        theme_map: Dictionary mapping theme names to keywords.
        top_k: Number of top themes to include.
        include_examples: Whether to include examples in the themes DataFrame.
        example_limit: Maximum number of examples per theme.
        openai_api_key: Your OpenAI API key.

    Returns:
        A tuple containing:
            - themes_df: DataFrame with theme summaries (Theme, Count, Examples).
            - theme_summaries: Dictionary with theme names as keys and ChatGPT summaries as values.
    """
    # Ensure the necessary helper functions are defined (assuming they are in the environment)
    if '_normalize_text' not in globals() or '_best_theme' not in globals():
         print("Error: Required helper functions (_normalize_text, _best_theme) are not defined.")
         return pd.DataFrame(), {}

    # 1. Group recommendations by theme using the existing function
    themes_df, _ = summarize_recommendations_to_themes(
        recommendations_df,
        theme_map=theme_map,
        top_k=top_k,
        include_examples=include_examples,
        example_limit=example_limit,
        markdown=False # No need for markdown summary at this stage
    )

    if themes_df.empty:
        print("No themes identified.")
        return themes_df, {}

    # Add the _theme column to the original recommendations_df for grouping
    df_themed = recommendations_df.copy()
    texts_for_theming = (
        df_themed.get("Recommendation", "").fillna("").astype(str)
        + " \n" + df_themed.get("Overview", "").fillna("").astype(str)
        + " \n" + df_themed.get("GMP Utilization Impact", "").fillna("").astype(str)
        + " \n" + df_themed.get("Business Impact", "").fillna("").astype(str)
    ).apply(_normalize_text)

    themes_for_df: List[str] = []
    current_theme_map = theme_map or _DEFAULT_THEME_MAP # Use default if none provided
    for t in texts_for_theming:
        theme, _ = _best_theme(t, current_theme_map)
        themes_for_df.append(theme)
    df_themed['_theme'] = themes_for_df

    # Group the original recommendations DataFrame by the new _theme column
    themed_recommendations = df_themed.groupby('_theme')

    # 2. Prepare data for ChatGPT
    recommendations_by_theme_text = {}
    for theme, group in themed_recommendations:
        theme_text = f"Theme: {theme}\nRecommendations:\n"
        for index, row in group.iterrows():
            theme_text += f"- Recommendation: {row.get('Recommendation', '')}\n"
            theme_text += f"  Overview: {row.get('Overview', '')}\n"
        recommendations_by_theme_text[theme] = theme_text

    # 3. Call ChatGPT API
    openai.api_key = openai_api_key
    theme_summaries = {}

    for theme, text in recommendations_by_theme_text.items():
        prompt = f"Summarize the following recommendations for the theme '{theme}':\n\n{text}"
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            summary = response.choices[0].message.content.strip()
            theme_summaries[theme] = summary
        except Exception as e:
            print(f"An error occurred while summarizing theme '{theme}': {e}")
            theme_summaries[theme] = f"Error summarizing theme: {e}"

    # 4. Present the summaries (optional - can be done outside the function)
    print("\n--- ChatGPT Summaries by Theme ---")
    for theme, summary in theme_summaries.items():
        print(f"## Theme: {theme}")
        print(f"{summary}")
        print("-" * 30) # Separator for clarity

    return themes_df, theme_summaries

# Note: This function relies on _normalize_text and _best_theme being defined
# in the environment where it is called. It also requires the OpenAI API key
# to be set correctly.


def summarize_recommendations_to_themes(
    recommendations_df: pd.DataFrame,
    theme_map: Optional[Dict[str, Iterable[str]]] = None,
    top_k: int = 6,
    include_examples: bool = True,
    example_limit: int = 3,
    markdown: bool = True,
) -> Tuple[pd.DataFrame, str]:
    """
    Group `recommendations_df` into a handful of key themes using a lightweight, keyword-based classifier.

    Expected columns (robust to missing):
      - 'Recommendation' (title)
      - 'Overview'
      - 'GMP Utilization Impact'
      - 'Business Impact'
      - 'Score', 'MaxWeight', 'Score %'

    Returns:
      (themes_df, summary_md)
        - themes_df columns: ['Theme','Count','Total Score','Total MaxWeight','Avg Score %','Examples']
        - summary_md: readable markdown summary (bullets grouped by theme)
    """
    if recommendations_df is None or recommendations_df.empty:
        empty = pd.DataFrame(columns=[
            "Theme", "Count", "Total Score", "Total MaxWeight", "Avg Score %", "Examples"
        ])
        return empty, ("No recommendations matched." if markdown else "No recommendations matched.")

    theme_map = theme_map or _DEFAULT_THEME_MAP

    df = recommendations_df.copy()
    # Ensure numeric fields exist
    for col in ("Score", "MaxWeight"):
        if col not in df.columns:
            df[col] = 0.0
    if "Score %" not in df.columns:
        df["Score %"] = df.apply(lambda x: (float(x.get("Score", 0)) / float(x.get("MaxWeight", 0))) * 100 if float(x.get("MaxWeight", 0)) else 0.0, axis=1)

    texts = (
        df.get("Recommendation", "").fillna("").astype(str)
        + " \n" + df.get("Overview", "").fillna("").astype(str)
        + " \n" + df.get("GMP Utilization Impact", "").fillna("").astype(str)
        + " \n" + df.get("Business Impact", "").fillna("").astype(str)
    ).apply(_normalize_text)

    # Classify to themes
    themes: List[str] = []
    scores: List[int] = []
    for t in texts:
        theme, score = _best_theme(t, theme_map)
        themes.append(theme)
        scores.append(score)
    df["_theme"] = themes
    df["_theme_score"] = scores

    # Aggregate
    agg = (
        df.groupby("_theme")
          .agg(Count=("_theme", "count"),
               **{"Total Score": ("Score", "sum"),
                  "Total MaxWeight": ("MaxWeight", "sum"),
                  "Avg Score %": ("Score %", "mean")})
          .reset_index()
          .rename(columns={"_theme": "Theme"})
    )
    agg["Avg Score %"] = agg["Avg Score %"].round(2)

    # Example titles per theme
    examples_map: Dict[str, List[str]] = {}
    if include_examples:
        for theme, sub in df.sort_values("_theme_score", ascending=False).groupby("_theme"):
            examples_map[theme] = sub["Recommendation"].fillna("").astype(str).head(example_limit).tolist()
        agg["Examples"] = agg["Theme"].map(lambda t: "; ".join(examples_map.get(t, [])))
    else:
        agg["Examples"] = ""

    # Rank & limit
    agg = agg.sort_values(["Count", "Total Score"], ascending=[False, False]).head(top_k)

    # Markdown summary
    if markdown:
        lines = ["**Key Recommendation Themes**"]
        for _, row in agg.iterrows():
            theme = row["Theme"]
            cnt = int(row["Count"]) if not pd.isna(row["Count"]) else 0
            total_score = float(row["Total Score"]) if not pd.isna(row["Total Score"]) else 0.0
            avg_pct = float(row["Avg Score %"]) if not pd.isna(row["Avg Score %"]) else 0.0
            examples = row.get("Examples", "")
            line = f"- **{theme}** — {cnt} recs | Avg score: {avg_pct:.1f}% | Total score: {total_score:.2f}"
            lines.append(line)
            if include_examples and examples:
                lines.append(f"  - _Examples_: {examples}")
        summary_md = "\n".join(lines)
    else:
        lines = ["Key Recommendation Themes"]
        for _, row in agg.iterrows():
            theme = row["Theme"]
            cnt = int(row["Count"]) if not pd.isna(row["Count"]) else 0
            total_score = float(row["Total Score"]) if not pd.isna(row["Total Score"]) else 0.0
            avg_pct = float(row["Avg Score %"]) if not pd.isna(row["Avg Score %"]) else 0.0
            examples = row.get("Examples", "")
            line = f"- {theme} — {cnt} recs | Avg score: {avg_pct:.1f}% | Total score: {total_score:.2f}"
            lines.append(line)
            if include_examples and examples:
                lines.append(f"  - Examples: {examples}")
        summary_md = "\n".join(lines)

    return agg.reset_index(drop=True), summary_md



def _truncate(text: str, max_len: int = 180) -> str:
    if text is None:
        return ""
    s = str(text).strip()
    return s if len(s) <= max_len else s[: max_len - 1].rstrip() + "…"


def summarize_maturity_gaps_to_df(
    gaps_df: pd.DataFrame,
    per_category_limit: int = 5,
    model_name: str = "gpt-4.1-mini",
    max_tokens: int = 1200
) -> pd.DataFrame:
    """
    Summarizes maturity gaps (from mat_gaps_df) into key themes per Category using OpenAI,
    returning a structured DataFrame: Category | Theme | Summary.
    """

    required_cols = {"Category", "Heading", "Context", "Impact"}
    if gaps_df is None or gaps_df.empty or not required_cols.issubset(gaps_df.columns):
        return pd.DataFrame(columns=["Category", "Theme", "Summary"])

    # Trim for brevity
    trimmed = (
        gaps_df
        .copy()
        .sort_values(["Category", "Heading"])
        .groupby("Category", dropna=False)
        .head(per_category_limit)
        .reset_index(drop=True)
    )

    # Group data for the prompt
    grouped = {}
    for cat, sub in trimmed.groupby("Category", dropna=False):
        cat_name = "Uncategorized" if pd.isna(cat) or str(cat).strip() == "" else str(cat)
        grouped[cat_name] = [
            {
                "heading": str(row["Heading"]).strip(),
                "context": str(row["Context"]).strip(),
                "impact": str(row["Impact"]).strip()
            }
            for _, row in sub.iterrows()
        ]

    prompt = f"""
You are an Adtech/Martech maturity consultant.

Summarize the following categorized marketing maturity gaps into clear themes.

For each Category, analyze the provided list of gaps (each has a heading, context, and impact) 
and summarize them into 2–4 **key themes** that capture the main issues or opportunities.

Return JSON ONLY in this exact format:
[
  {{
    "Category": "<Category Name>",
    "Theme": "<Short Theme Name>",
    "Summary": "<2–3 sentence summary combining related gaps>"
  }},
  ...
]

Do not include any text before or after the JSON.

GAPS DATA (JSON):
{json.dumps(grouped, ensure_ascii=False, indent=2)}
"""

    client = openai.OpenAI(api_key=st.secrets["OPEN_AI_KEY"])
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a marketing maturity consultant summarizing audit gaps into concise structured insights."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=max_tokens,
    )

    text = response.choices[0].message.content.strip()

    # --- Parse JSON safely ---
    try:
        parsed = json.loads(text)
        mat_gaps_summary_df = pd.DataFrame(parsed)
    except json.JSONDecodeError:
        # fallback: return one-row DF with raw text
        mat_gaps_summary_df = pd.DataFrame(
            [{"Category": "Parsing Error", "Theme": "N/A", "Summary": text}]
        )

    return mat_gaps_summary_df


def matched_recs_to_df(results: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert the dict returned by run_recommendation_analysis(...) into a tidy DataFrame
    that’s convenient for Streamlit tables and for feeding into the PDF builder.

    Columns:
    - Recommendation
    - Overview
    - GMP Utilization Impact
    - Business Impact
    - Score
    - MaxWeight
    - Score %
    """
    recs = results.get("matched_recommendations", []) or []
    rows = []
    for r in recs:
        rows.append(
            {
                "Recommendation": r.get("recommendation", ""),
                "Overview": r.get("overview", ""),
                "GMP Utilization Impact": r.get("gmp_impact", ""),
                "Business Impact": r.get("business_impact", ""),
                "Score": float(r.get("score", 0.0) or 0.0),
                "MaxWeight": float(r.get("maxweight", 0.0) or 0.0),
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty:
        # Avoid divide-by-zero; show percentage to 2dp
        df["Score %"] = (
            df.apply(lambda x: (x["Score"] / x["MaxWeight"]) * 100 if x["MaxWeight"] else 0.0, axis=1)
            .round(2)
        )
    else:
        df = pd.DataFrame(
            columns=[
                "Recommendation",
                "Overview",
                "GMP Utilization Impact",
                "Business Impact",
                "Score",
                "MaxWeight",
                "Score %",
            ]
        )
    return df
