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
    },
    {
        "set_id": "CDP_Opt_Cons",
        "questions": [
            {
                "question": "Which of the following use cases is your Customer Data Platform (CDP) currently being used for? (select all that apply)",
                 "match_criteria": {
                 "min_matches": 4,
              "or_group": ["Personalized Recommendations. Using behavioral and transactional data to serve personalized, dynamic, context-aware offers or products.","Intelligent Enrichment. Enrich audience segments with AI/ML model insights such as propensity scoring or sentiment analysis.","Omnichannel Journey Orchestration. Coordinating consistent, deduplicated, messaging across email, paid media, SMS, push and web.","Automated Triggers & Journey. Trigger real-time communications based on user behavior or lifecycle stage.","Retention & Loyalty Programs. Track loyalty tiers, reward points, and re-engage dormant users using predictive insights.","Churn Reduction & Lifetime Value Prediction. Identify at-risk customers and optimize for higher customer lifetime value.","Monetization of O&O. Powering retail media and/or partner activation across owned & operated channels and/or 1st party audiences","Consent & Privacy Management. Managing user consent preferences and ensure compliance with data privacy regulations.","Geo Targeting. Adapting experiences and offers based on user location, region, or local regulations.","Other"]
            }
            },
            {
                "question": "Overall, how well is your Customer Data Platform (CDP) meeting your organization’s expectations in delivering the required audience strategy use cases?",
                "answer": ["Partially meeting expectations","Not meeting expectations"]
            },
            {
                "question": "Do you have a Customer Data Platform (CDP)?",
                "answer": ["Yes"]
            }
        ],
        "recommendation": "CDP Optimization Consultancy",
        "overview": "We recommend conducting a review of existing CDP use cases to ensure they are delivering full value and to identify opportunities to expand the range of active use cases, increasing the overall potential of the CDP. The review should focus on underutilized capabilities to unlock new opportunities for personalization, measurement, and automation. This approach ensures your CDP operates as a strategic growth driver, maximizing the return on your technology investment."
    },
   {
        "set_id": "CDP_Assess",
        "questions": [
            {
                "question": "Do you have a Customer Data Platform (CDP)?",
                "answer": ["No, we are unsure whether or not a CDP is required at this time","No, we have explored the need for a CDP and not determined whether or not we require one"]
            },
            {
                "question": "Which of the following Audience Strategy use cases would your organization benefit from, but is not currently undertaking? (Select all that apply)",
                "answer": ["None of the above"],
                "type": "negative_choice"
            }    
        ],
        "recommendation": "CDP Readiness",
        "overview": "We recommend undertaking a comprehensively exploring CDP readiness, to determine whether a CDP  is required for desired use cases, or if existing technologies can be optimized to deliver similar capabilities. Identification of technology gaps, integration opportunities and use case priorities can inform investment decisions and establish a clear roadmap for value realization. This ensures resources are directed toward the most effective solution, whether through CDP adoption, enhancement of existing systems, or a hybrid approach."
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
    and return only the matched recommendations (no scores or totals).
    """
    csv_data_map = {}
    for index, row in df.iterrows():
        question_key = str(row['Question']).lower().strip()
        answer_value = normalize_answer_for_comparison(row['Answer'])

        # Handle multiple answers per question
        if question_key not in csv_data_map:
            csv_data_map[question_key] = {'answers': [answer_value]}
        else:
            csv_data_map[question_key]['answers'].append(answer_value)

    matched_recommendations = []

    if 'RECOMMENDATION_SET' not in globals():
        print("Error: RECOMMENDATION_SET is not defined.")
        return {'matched_recommendations': []}

    for item in RECOMMENDATION_SET:
        if "set_id" not in item:
            # --- Single Question Recommendation ---
            if 'question' not in item or 'answer' not in item:
                continue

            rec_question = item['question'].lower().strip()
            rec_answer_raw = item['answer']
            rec_recommendation = item['recommendation']
            rec_overview = item.get('overview', 'N/A')
            rec_gmp_impact = item.get('gmpimpact', 'N/A')
            rec_business_impact = item.get('businessimpact', 'N/A')
            rec_type = item.get('type')

            csv_entry = csv_data_map.get(rec_question)
            user_answers = csv_entry['answers'] if csv_entry else []
            current_condition_met = False

            if user_answers:
                normalized_rec_answers = (
                    [normalize_answer_for_comparison(a) for a in rec_answer_raw]
                    if isinstance(rec_answer_raw, list)
                    else [normalize_answer_for_comparison(rec_answer_raw)]
                )

                if rec_type == "negative_choice":
                    current_condition_met = all(
                        ans not in normalized_rec_answers for ans in user_answers
                    )
                else:
                    current_condition_met = any(
                        ans in normalized_rec_answers for ans in user_answers
                    )

            if current_condition_met:
                matched_recommendations.append({
                    'recommendation': rec_recommendation,
                    'overview': rec_overview,
                    'gmp_impact': rec_gmp_impact,
                    'business_impact': rec_business_impact
                })

        else:
            # --- Grouped Question Recommendation ---
            group_recommendation = item['recommendation']
            rec_overview = item.get('overview', 'N/A')
            rec_gmp_impact = item.get('gmpimpact', 'N/A')
            rec_business_impact = item.get('businessimpact', 'N/A')

            group_condition_met = False

            # Match based on grouped logic
            if 'match_answers_from_questions' in item and len(item['match_answers_from_questions']) == 2:
                q1_key = item['match_answers_from_questions'][0].lower().strip()
                q2_key = item['match_answers_from_questions'][1].lower().strip()
                q1_entry = csv_data_map.get(q1_key)
                q2_entry = csv_data_map.get(q2_key)

                if q1_entry and q2_entry:
                    q1_answers = q1_entry['answers']
                    q2_answers = q2_entry['answers']
                    if q1_answers and q2_answers and q1_answers[0] == q2_answers[0] and q1_answers[0] != "":
                        group_condition_met = True
            else:
                group_questions = item.get('questions', [])
                matches = []
                for sub_q in group_questions:
                    if 'question' not in sub_q or 'answer' not in sub_q:
                        continue
                    sub_q_key = sub_q['question'].lower().strip()
                    sub_q_answer_raw = sub_q['answer']
                    sub_q_type = sub_q.get('type')
                    csv_sub_q_entry = csv_data_map.get(sub_q_key)
                    user_answers = csv_sub_q_entry['answers'] if csv_sub_q_entry else []
                    current_sub_match = False

                    if user_answers:
                        normalized_sub_q_answers = (
                            [normalize_answer_for_comparison(a) for a in sub_q_answer_raw]
                            if isinstance(sub_q_answer_raw, list)
                            else [normalize_answer_for_comparison(sub_q_answer_raw)]
                        )

                        if sub_q_type == "negative_choice":
                            current_sub_match = all(
                                ans not in normalized_sub_q_answers for ans in user_answers
                            )
                        else:
                            current_sub_match = any(
                                ans in normalized_sub_q_answers for ans in user_answers
                            )

                    if current_sub_match:
                        matches.append(True)

                min_matches_required = item.get('min_matches')
                is_or_group = item.get('or_group')

                if min_matches_required is not None:
                    group_condition_met = len(matches) >= min_matches_required
                elif is_or_group:
                    group_condition_met = len(matches) > 0
                else:
                    group_condition_met = len(matches) == len(group_questions)

            if group_condition_met:
                matched_recommendations.append({
                    'recommendation': group_recommendation,
                    'overview': rec_overview,
                    'gmp_impact': rec_gmp_impact,
                    'business_impact': rec_business_impact
                })

    return {'matched_recommendations': matched_recommendations}



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

    GAP_DRIVER_PATTERN = re.compile(
    r"^\s*([^\*]+?)\s*\*\*\s*Context\s*\*\*\s*:\s*(.*?)\s*\*\*\s*Impact\s*\*\*\s*:\s*(.*?)$",
    re.DOTALL | re.IGNORECASE
    )
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

Reviewing the questions and answers, and (if provided) comments below, identify the most critical **marketing maturity gaps** for this category.
A "maturity gap" is a disconnect between the current state and a more advanced, effective stage of marketing capability.

Anchor your thinking to these three pillars:
1) Identify & Eliminate Inefficiencies — overlaps, gaps, and underutilized capabilities across platforms, data, and tech; streamline architecture; reduce wasted investment.
2) Accelerate Innovation & Maturity — expose gaps blocking growth; introduce new tools, approaches, or AI-led solutions to keep pace with market shifts.
3) Develop a Sustainable Growth Roadmap — translate insights into a prioritized, achievable plan with resourcing, so gains are implemented and sustained.

For each gap, return:
Each maturity gap should include:
- A concise **Heading** (e.g., "Lack of First-Party Data Activation")
- A brief 25 words or less **Context** (what the maturity driver is and why it matters)
- A clear 25 words or less **Impact** (how this gap is affecting the advertiser's performance or strategic outcomes)

Output strictly as a numbered list:
1. **Heading**: ...
   **Context**: ...
   **Impact**: ...

Questions: {questions}
Answers: {answers}
Comments: {comments}
        """.strip()

        try:
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
        except Exception as e:
            print(f"Error calling OpenAI API for category '{cat}': {e}")
            text = "" # Skip parsing if API call failed

        # --- REVISED PARSING LOGIC ---
        gaps = []
        # Split by the gap number and Heading label to isolate each gap
        parts = re.split(r'\n?\s*\d+\.\s*\*\*Heading\*\*\s*:\s*', text)

        for chunk in parts[1:]: # Skip the first part (preamble)
            match = GAP_DRIVER_PATTERN.search(chunk.strip())

            if match:
                # Groups: 1=Heading, 2=Context, 3=Impact
                gaps.append({
                    "Category": cat,
                    "Heading": match.group(1).strip() or "N/A",
                    "Context": match.group(2).strip() or "N/A",
                    "Impact": match.group(3).strip() or "N/A",
                })
            else:
                 # Fallback for completely unparseable chunk
                 gaps.append({
                    "Category": cat,
                    "Heading": f"Parsing Failed (Chunk: {chunk[:50]}...)",
                    "Context": "N/A",
                    "Impact": "N/A",
                })
        # -----------------------------

        all_rows.extend(gaps)

    mat_gaps_df = pd.DataFrame(all_rows, columns=["Category", "Heading", "Context", "Impact"])

    # Drop empty/failed rows
    if not mat_gaps_df.empty:
        mask_empty = mat_gaps_df[["Heading", "Context", "Impact"]].apply(
            lambda r: all((str(x).strip() in {"", "N/A"}) for x in r), axis=1
        )
        mat_gaps_df = mat_gaps_df[~mask_empty].reset_index(drop=True)

    return mat_gaps_df


 
def _parse_drivers_from_text(category: str, text: str) -> List[dict]:
    """
    Robustly parse numbered blocks like:
      1. **Heading**: ...
         **Context**: ...
         **Impact**: ...
    Accepts missing **, extra spaces, or line-break variation.
    """
    if not text:
        return []

    s = _strip_code_fences(text).strip()

    # 1) Split into item blocks by numbered prefix "1.", "2.", ...
    #    We capture the entire block up to next number or end of string.
    item_pattern = re.compile(
        r'^\s*(\d+)\.\s*(.*?)(?=^\s*\d+\.|\Z)',  # block per numbered item
        flags=re.DOTALL | re.MULTILINE
    )

    # 2) Inside each block, extract Heading/Context/Impact with tolerant labels
    #    - allow optional **, any spaces, case-insensitive, punctuation
    label = r'(?:\*\*)?'           # optional starting **
    sep = r'[:：]\s*'              # colon variants + spaces
    heading_pat = re.compile(rf'{label}Heading(?:\*\*)?\s*{sep}(.*)', re.IGNORECASE | re.DOTALL)
    context_pat = re.compile(rf'{label}Context(?:\*\*)?\s*{sep}(.*)', re.IGNORECASE | re.DOTALL)
    impact_pat  = re.compile(rf'{label}Impact(?:\*\*)?\s*{sep}(.*)',  re.IGNORECASE | re.DOTALL)

    # Helper to slice a block into fields by looking ahead to the next label
    def extract_field(block: str, start_pat: re.Pattern, next_pats: List[re.Pattern]) -> str:
        m = start_pat.search(block)
        if not m:
            return ""
        start = m.end()
        # find the earliest next label after start to delimit this field
        next_indices = []
        for p in next_pats:
            n = p.search(block, pos=start)
            if n:
                next_indices.append(n.start())
        end = min(next_indices) if next_indices else len(block)
        return block[start:end].strip()

    rows = []
    for _m in item_pattern.finditer(s):
        block = _m.group(2).strip()

        # Normalize line breaks to make parsing less finicky
        block_norm = re.sub(r'\r\n?', '\n', block)

        heading = extract_field(block_norm, heading_pat, [context_pat, impact_pat])
        context = extract_field(block_norm, context_pat, [impact_pat])
        impact  = extract_field(block_norm, impact_pat, [])

        # Fallbacks: if no labeled heading, take first non-empty line as heading
        if not heading:
            first_line = next((ln.strip() for ln in block_norm.splitlines() if ln.strip()), "")
            heading = first_line

        rows.append({
            "Category": category,
            "Heading": heading or "N/A",
            "Context": context or "N/A",
            "Impact":  impact  or "N/A",
        })

    return rows

GAP_DRIVER_PATTERN = re.compile(
    r"^\s*([^\*]+?)\s*\*\*\s*Context\s*\*\*\s*:\s*(.*?)\s*\*\*\s*Impact\s*\*\*\s*:\s*(.*?)$",
    re.DOTALL | re.IGNORECASE
)

def identify_top_maturity_drivers(
    df: pd.DataFrame,
    model_name: str = "gpt-4.1-mini",
    max_tokens: int = 1200
) -> pd.DataFrame:
    """
    Generate maturity Drivers PER CATEGORY using the 'Category' column.
    Returns a DataFrame with columns: Category, Heading, Context, Impact.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["Category", "Heading", "Context", "Impact"])

    for col in ["Category", "Question", "Answer"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    has_comments = "Comment" in df.columns
    all_rows: List[dict] = []

    categories = (
        df["Category"].apply(lambda x: "" if pd.isna(x) else str(x)).unique().tolist()
    )
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
You are a strategic Adtech/Martech advisor assessing an advertiser’s maturity.

Focus ONLY on the Category: "{cat}".

Reviewing the questions and answers, and (if provided) comments below, identify the most critical **marketing maturity drivers** for this category.
A "maturity driver" is something that the business is currently doing well that accounts for their current level of marketing maturity, focused on their Google Marketing Platform usage.

Each maturity driver should include:
- A concise **Heading** (e.g., "Integration of First-Party Data")
- A brief 25 words or less **Context** (what the maturity driver is and why it matters)
- A clear 25 words or less **Impact** (how this driver improves the advertiser's maturity or strategic outcomes)

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
                {"role": "system", "content": "You are a marketing maturity consultant identifying key capability drivers from audits."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.6,
        )

        text = resp.choices[0].message.content if resp and resp.choices else ""

        parsed_rows = []
        # Split by the driver number and Heading label to isolate each driver
        parts = re.split(r'\n?\s*\d+\.\s*\*\*Heading\*\*\s*:\s*', text)

        for chunk in parts[1:]: # Skip the first part (preamble)
            match = GAP_DRIVER_PATTERN.search(chunk.strip())

            if match:
                # Groups: 1=Heading, 2=Context, 3=Impact
                parsed_rows.append({
                    "Category": cat,
                    "Heading": match.group(1).strip() or "N/A",
                    "Context": match.group(2).strip() or "N/A",
                    "Impact": match.group(3).strip() or "N/A",
                })
            else:
                 # Fallback for completely unparseable chunk
                 # (Optional: Can remove this fallback if clean output is strictly required)
                 pass

        all_rows.extend(parsed_rows)
        # --------------------------------------------------

    maturity_drivers_df = pd.DataFrame(all_rows, columns=["Category", "Heading", "Context", "Impact"])

    # Remove rows where all fields are effectively empty/N/A
    # Drop empty/failed rows
    if not maturity_drivers_df.empty:
        mask_empty = maturity_drivers_df[["Heading", "Context", "Impact"]].apply(
            lambda r: all((str(x).strip() in {"", "N/A"}) for x in r), axis=1
        )
        maturity_drivers_df = maturity_drivers_df[~mask_empty].reset_index(drop=True)

    return maturity_drivers_df


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
    openai_api_key: str = "YOUR_API_KEY"
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Groups recommendations by theme, gets summaries from ChatGPT, and returns
    the themes DataFrame and a dictionary of theme summaries.
    """

    if '_normalize_text' not in globals() or '_best_theme' not in globals():
        print("Error: Required helper functions (_normalize_text, _best_theme) are not defined.")
        return pd.DataFrame(), {}

    # 1) Group to themes (uses updated no-score version below)
    themes_df, _ = summarize_recommendations_to_themes(
        recommendations_df,
        theme_map=theme_map,
        top_k=top_k,
        include_examples=include_examples,
        example_limit=example_limit,
        markdown=False
    )
    if themes_df.empty:
        print("No themes identified.")
        return themes_df, {}

    # --- Helper to pull a Series safely regardless of column naming ---
    def _col_series(df: pd.DataFrame, candidates: List[str]) -> pd.Series:
        for c in candidates:
            if c in df.columns:
                return df[c].fillna("").astype(str)
        return pd.Series([""] * len(df), index=df.index)

    # Normalize/alias columns for theming text (Title Case or snake_case both OK)
    df_themed = recommendations_df.copy()
    rec_ser  = _col_series(df_themed, ["Recommendation", "recommendation"])
    over_ser = _col_series(df_themed, ["Overview", "overview"])
    gmp_ser  = _col_series(df_themed, ["GMP Utilization Impact", "gmp_impact"])
    biz_ser  = _col_series(df_themed, ["Business Impact", "business_impact"])

    texts_for_theming = (rec_ser + " \n" + over_ser + " \n" + gmp_ser + " \n" + biz_ser).apply(_normalize_text)

    # Classify each row to a theme (using your keyword map)
    current_theme_map = theme_map or _DEFAULT_THEME_MAP
    themes_for_df: List[str] = []
    for t in texts_for_theming:
        theme, _ = _best_theme(t, current_theme_map)
        themes_for_df.append(theme)
    df_themed["_theme"] = themes_for_df

    # Group original recommendations by inferred theme
    themed_recommendations = df_themed.groupby("_theme")

    # 2) Prepare per-theme text for the LLM
    recommendations_by_theme_text: Dict[str, str] = {}
    for theme, group in themed_recommendations:
        lines = [f"Theme: {theme}", "Recommendations:"]
        for _, row in group.iterrows():
            lines.append(f"- Recommendation: {row.get('Recommendation', row.get('recommendation', ''))}")
            lines.append(f"  Overview: {row.get('Overview', row.get('overview', ''))}")
        recommendations_by_theme_text[theme] = "\n".join(lines)

    # 3) Call OpenAI for summaries
    openai.api_key = openai_api_key
    theme_summaries: Dict[str, str] = {}
    for theme, text in recommendations_by_theme_text.items():
        prompt = f"Summarize the following recommendations for the theme '{theme}':\n\n{text}"
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a digital marketing assistant that specializes in martech and adtech recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            summary = response.choices[0].message.content.strip()
            theme_summaries[theme] = summary
        except Exception as e:
            print(f"An error occurred while summarizing theme '{theme}': {e}")
            theme_summaries[theme] = f"Error summarizing theme: {e}"

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
    Group recommendations into key themes using a lightweight, keyword-based classifier.

    Expected columns (robust to missing / aliasing):
      - 'Recommendation' / 'recommendation'
      - 'Overview' / 'overview'
      - 'GMP Utilization Impact' / 'gmp_impact'
      - 'Business Impact' / 'business_impact'

    Returns:
      (themes_df, summary_md)
        - themes_df columns: ['Theme','Count','Examples']
        - summary_md: readable summary (no score references)
    """
    if recommendations_df is None or recommendations_df.empty:
        empty = pd.DataFrame(columns=["Theme", "Count", "Examples"])
        return empty, ("No recommendations matched." if markdown else "No recommendations matched.")

    theme_map = theme_map or _DEFAULT_THEME_MAP
    df = recommendations_df.copy()

    # Helpers to safely fetch text series
    def _col_series(df_: pd.DataFrame, candidates: List[str]) -> pd.Series:
        for c in candidates:
            if c in df_.columns:
                return df_[c].fillna("").astype(str)
        return pd.Series([""] * len(df_), index=df_.index)

    rec_ser  = _col_series(df, ["Recommendation", "recommendation"])
    over_ser = _col_series(df, ["Overview", "overview"])
    gmp_ser  = _col_series(df, ["GMP Utilization Impact", "gmp_impact"])
    biz_ser  = _col_series(df, ["Business Impact", "business_impact"])

    texts = (rec_ser + " \n" + over_ser + " \n" + gmp_ser + " \n" + biz_ser).apply(_normalize_text)

    # Classify to themes
    themes: List[str] = []
    scores_for_rank: List[int] = []  # classifier confidence only, not shown
    for t in texts:
        theme, score = _best_theme(t, theme_map)
        themes.append(theme)
        scores_for_rank.append(score)
    df["_theme"] = themes
    df["_theme_score"] = scores_for_rank

    # Aggregate (Count only; no score fields)
    agg = (
        df.groupby("_theme")
          .agg(Count=("_theme", "count"))
          .reset_index()
          .rename(columns={"_theme": "Theme"})
    )

    # Example titles per theme
    if include_examples:
        examples_map: Dict[str, List[str]] = {}
        for theme, sub in df.sort_values("_theme_score", ascending=False).groupby("_theme"):
            examples_map[theme] = sub.get("Recommendation", sub.get("recommendation", pd.Series([], dtype=str)))\
                                     .fillna("").astype(str).head(example_limit).tolist()
        agg["Examples"] = agg["Theme"].map(lambda t: "; ".join(examples_map.get(t, [])))
    else:
        agg["Examples"] = ""

    # Rank & limit (by Count, then classifier score as tiebreaker)
    agg = agg.sort_values(["Count"], ascending=[False]).head(top_k).reset_index(drop=True)

    # Summary (no score wording)
    if markdown:
        lines = ["**Key Recommendation Themes**"]
        for _, row in agg.iterrows():
            theme = row["Theme"]
            cnt = int(row["Count"]) if not pd.isna(row["Count"]) else 0
            examples = row.get("Examples", "")
            line = f"- **{theme}** — {cnt} recs"
            lines.append(line)
            if include_examples and examples:
                lines.append(f"  - _Examples_: {examples}")
        summary_md = "\n".join(lines)
    else:
        lines = ["Key Recommendation Themes"]
        for _, row in agg.iterrows():
            theme = row["Theme"]
            cnt = int(row["Count"]) if not pd.isna(row["Count"]) else 0
            examples = row.get("Examples", "")
            line = f"- {theme} — {cnt} recs"
            lines.append(line)
            if include_examples and examples:
                lines.append(f"  - Examples: {examples}")
        summary_md = "\n".join(lines)

    return agg[["Theme", "Count", "Examples"]].reset_index(drop=True), summary_md


def _coerce_json_array(text: str) -> str:
    s = text.strip()
    if s.startswith('[') and s.endswith(']'):
        return s
    m = re.search(r"\[.*\]", s, re.DOTALL)
    return m.group(0) if m else s



def _parse_json_array_from_text(raw: str) -> List[dict]:
    candidate = _strip_code_fences(raw)
    candidate = _coerce_json_array(candidate)
    candidate = _light_json_sanitize(candidate)
    data = json.loads(candidate)
    if not isinstance(data, list):
        raise ValueError("Parsed JSON is not a list.")
    return data


def _truncate_text(text: str, max_len: int = 180) -> str:
    if text is None:
        return ""
    s = str(text).strip()
    return s if len(s) <= max_len else s[: max_len - 1].rstrip() + "…"



def _strip_code_fences(text: str) -> str:
    """
    Strips ```json ... ``` or ``` ... ``` fences if present.
    """
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    return fence_match.group(1) if fence_match else text

def _coerce_json_array(text: str) -> str:
    """
    Attempts to isolate the first JSON array substring in the text.
    If the whole text is an array, returns it as-is.
    Otherwise, finds the first '[' and the matching last ']' greedily.
    """
    s = text.strip()
    if s.startswith('[') and s.endswith(']'):
        return s

    # Try finding a fenced or embedded array
    m = re.search(r"\[.*\]", s, re.DOTALL)
    if m:
        return m.group(0)

    # Fallback: return original (will likely fail json.loads and be handled)
    return s

def _light_json_sanitize(text: str) -> str:
    s = (text.replace("\u201c", "\"")
             .replace("\u201d", "\"")
             .replace("\u2019", "'")
             .replace("\xa0", " "))
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s

def _parse_json_array_from_text(sum_text: str) -> list:
    """
    Best-effort parse of a JSON array from model output.
    Raises ValueError if parsing fails.
    """
    candidate = _strip_code_fences(sum_text)
    candidate = _coerce_json_array(candidate)
    candidate = _light_json_sanitize(candidate)
    data = json.loads(candidate)  # let it raise if invalid
    if not isinstance(data, list):
        raise ValueError("Parsed JSON is not a list.")
    return data

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
    "Summary": "<2–3 sentences summary combining related gaps>"
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

    sum_text = response.choices[0].message.content.strip()

    # --- Parse JSON safely (robust) ---
    try:
        parsed = _parse_json_array_from_text(sum_text)
    except Exception as e:
        # If parsing fails, return an empty df but keep a clue in logs
        print(f"Failed to parse JSON from model output: {e}\nRaw output:\n{sum_text[:1000]}")
        return pd.DataFrame(columns=["Category", "Theme", "Summary"])

    # Normalize into DataFrame
    rows = []
    for rec in parsed:
        # Be defensive about keys
        cat = (rec.get("Category") or "").strip()
        theme = (rec.get("Theme") or "").strip()
        summ = (rec.get("Summary") or "").strip()
        if cat or theme or summ:
            rows.append({"Category": cat, "Theme": theme, "Summary": summ})

    mat_gaps_summary_df = pd.DataFrame(rows, columns=["Category", "Theme", "Summary"])
    return mat_gaps_summary_df


def matched_recs_to_df(results: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert the dict returned by run_recommendation_analysis(...) into a tidy DataFrame.

    Columns:
    - Recommendation
    - Overview
    - GMP Utilization Impact
    - Business Impact
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
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(
            columns=[
                "Recommendation",
                "Overview",
                "GMP Utilization Impact",
                "Business Impact",
            ]
        )
    return df


def gaps_summary_df_to_markdown(df: pd.DataFrame) -> str:
    """
    Convert the Category|Theme|Summary DataFrame into readable Markdown.
    Groups by Category and lists each theme and summary beneath it.
    Example output:

    ### Maturity Gap Themes

    **Audience Strategy**
    - **Data Fragmentation** — Audience data is siloed across multiple tools, limiting personalization.
    - **Limited Activation** — Current workflows underutilize 1P data for lookalike modeling.

    **Measurement**
    - **Attribution Gaps** — Reporting lacks multi-touch attribution or post-click tracking.
    """
    if df is None or df.empty:
        return "_No summarized maturity gaps available._"

    lines = ["### Maturity Gap Themes"]

    # Group by Category and format each theme under its category
    for cat, sub in df.groupby("Category", dropna=False):
        cat_name = "Uncategorized" if pd.isna(cat) or str(cat).strip() == "" else str(cat)
        lines.append(f"\n**{cat_name}**")

        for _, row in sub.iterrows():
            theme = str(row.get("Theme", "")).strip()
            summary = str(row.get("Summary", "")).strip()
            if theme:
                lines.append(f"- **{theme}** — {summary}")
            elif summary:
                lines.append(f"- {summary}")

    return "\n".join(lines)


def alignment_df_to_markdown(align_df: pd.DataFrame) -> str:
    """
    Render recommendation→gap alignment DataFrame as Markdown.
    Groups by recommendation and lists matched gaps with confidence, rationale, and explanation.
    """
    if align_df is None or align_df.empty:
        return "_No alignment results available._"

    lines: List[str] = ["### Recommendation → Gap Alignment"]
    for rec_id, sub in align_df.groupby("rec_id", sort=False):
        rec_text = sub["recommendation"].iloc[0] if "recommendation" in sub.columns else rec_id
        lines.append(f"\n**{rec_id} – {rec_text}**")
        if sub["gap_id"].fillna("").eq("").all():
            lines.append("- _No strong matching gap identified._")
        else:
            for _, row in sub.iterrows():
                gid = row.get("gap_id", "")
                gcat = row.get("gap_category", "")
                ghead = row.get("gap_heading", "")
                conf = row.get("confidence", "")
                how = row.get("how_it_addresses", "")
                rat = row.get("rationale", "")
                label = f"{gid} – {gcat}: {ghead}" if gid else "No Match"
                conf_str = f" (confidence {conf:.2f})" if isinstance(conf, (int, float)) else ""
                lines.append(f"- **{label}**{conf_str}\n  - *How it addresses:* {how}\n  - *Rationale:* {rat}")
    return "\n".join(lines)



# ---------- Helpers ----------



# ---------- Main Alignment Function ----------

def align_recommendations_to_gaps(
    rec_results: Dict[str, Any],
    gaps_df: pd.DataFrame,
    model_name: str = "gpt-4.1-mini",
    max_tokens: int = 1600,
    per_rec_max_gaps: int = 2,
    openai_api_key: Optional[str] = None,
) -> pd.DataFrame:
    """
    Uses GPT to match each recommendation to the most relevant maturity gaps.
    Inputs:
      - rec_results: dict from run_recommendation_analysis(...) with key 'matched_recommendations'
        Each recommendation supports keys: recommendation, overview
      - gaps_df: DataFrame with columns: ['Category','Heading','Context','Impact']
    Returns:
      pd.DataFrame with columns:
        ['rec_id','recommendation','gap_id','gap_category','gap_heading','confidence','how_it_addresses','rationale']
    """

    recs = rec_results.get("matched_recommendations", []) or []
    required_gap_cols = {"Category", "Heading", "Context", "Impact"}
    if not recs or gaps_df is None or gaps_df.empty or not required_gap_cols.issubset(gaps_df.columns):
        return pd.DataFrame(columns=[
            "rec_id","recommendation","gap_id","gap_category","gap_heading","confidence","how_it_addresses","rationale"
        ])

    # Build compact JSON payloads
    rec_items = []
    for i, r in enumerate(recs, start=1):
        rec_items.append({
            "id": f"R{i}",
            "recommendation": _truncate_text(r.get("recommendation", ""), 600),
            "overview": _truncate_text(r.get("overview", ""), 800),
        })

    gap_items = []
    for j, row in gaps_df.reset_index(drop=True).iterrows():
        gap_items.append({
            "id": f"G{j+1}",
            "category": _truncate_text(row.get("Category", ""), 120),
            "heading": _truncate_text(row.get("Heading", ""), 200),
            "context": _truncate_text(row.get("Context", ""), 500),
            "impact": _truncate_text(row.get("Impact", ""), 500),
        })

    # Prompt (simplified)
    prompt = f"""
You are a senior Adtech/Martech consultant.
Match each recommendation to the most relevant maturity gaps.

INSTRUCTIONS:
- Base matching on the recommendation text and its overview.
- For each recommendation, return up to {per_rec_max_gaps} best matching gap IDs (or [] if none).
- Provide a brief rationale and how the recommendation addresses those gaps.
- Confidence: 0.0–1.0 (float).

Return JSON ONLY in this schema:
[
  {{
    "rec_id": "R1",
    "matched_gap_ids": ["G2","G5"],
    "confidence": 0.86,
    "rationale": "Why these gaps match this recommendation.",
    "how_it_addresses": "What the recommendation changes to resolve the gap(s)."
  }},
  ...
]

GAPS (JSON):
{json.dumps(gap_items, ensure_ascii=False)}

RECOMMENDATIONS (JSON):
{json.dumps(rec_items, ensure_ascii=False)}
""".strip()

    api_key = openai_api_key or st.secrets.get("OPEN_AI_KEY")
    client = openai.OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You align marketing recommendations to identified maturity gaps, providing clear reasoning."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=max_tokens,
    )

    raw = resp.choices[0].message.content.strip()

    # Parse JSON
    try:
        parsed = _parse_json_array_from_text(raw)
    except Exception as e:
        print(f"[align_recommendations_to_gaps] Failed to parse JSON: {e}\nOutput head:\n{raw[:1000]}")
        return pd.DataFrame(columns=[
            "rec_id","recommendation","gap_id","gap_category","gap_heading","confidence","how_it_addresses","rationale"
        ])

    rec_map = {r["id"]: r for r in rec_items}
    gap_map = {g["id"]: g for g in gap_items}

    # Flatten
    rows = []
    for item in parsed:
        rec_id = str(item.get("rec_id", "")).strip()
        if not rec_id or rec_id not in rec_map:
            continue
        matched_ids = item.get("matched_gap_ids") or []
        conf = item.get("confidence", "")
        rationale = str(item.get("rationale", "")).strip()
        how = str(item.get("how_it_addresses", "")).strip()
        if isinstance(matched_ids, str):
            matched_ids = [matched_ids]

        if not matched_ids:
            rows.append({
                "rec_id": rec_id,
                "recommendation": rec_map[rec_id]["recommendation"],
                "gap_id": "",
                "gap_category": "",
                "gap_heading": "",
                "confidence": conf if isinstance(conf, (int, float)) else "",
                "how_it_addresses": how,
                "rationale": rationale,
            })
        else:
            for gid in matched_ids[:per_rec_max_gaps]:
                g = gap_map.get(gid)
                rows.append({
                    "rec_id": rec_id,
                    "recommendation": rec_map[rec_id]["recommendation"],
                    "gap_id": gid,
                    "gap_category": g.get("category", "") if g else "",
                    "gap_heading": g.get("heading", "") if g else "",
                    "confidence": conf if isinstance(conf, (int, float)) else "",
                    "how_it_addresses": how,
                    "rationale": rationale,
                })

    return pd.DataFrame(rows, columns=[
        "rec_id","recommendation","gap_id","gap_category","gap_heading","confidence","how_it_addresses","rationale"
    ])
