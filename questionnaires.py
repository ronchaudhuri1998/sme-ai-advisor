"""
Questionnaire definitions — common + industry-specific.

Each question dict:
    id      – unique key
    label   – display text
    type    – select | multiselect | slider | radio | text
    options – list of choices  (select / multiselect / radio)
    min/max – range bounds     (slider)
    help    – tooltip text shown via ℹ️ icon
"""

# ═══════════════════════════════════════════════════════════════════════
# COMMON QUESTIONS  (shown to every industry)
# ═══════════════════════════════════════════════════════════════════════
COMMON_QUESTIONS = [
    {
        "id": "company_size",
        "label": "How many employees does your company have?",
        "type": "select",
        "options": ["Under 50", "50–200", "200–500", "500–1,000", "1,000+"],
        "help": "Larger companies can typically support more complex AI infrastructure. Smaller teams benefit from fully managed cloud AI services.",
    },
    {
        "id": "num_locations",
        "label": "How many physical locations / sites does your business operate?",
        "type": "select",
        "options": ["1", "2–3", "4–10", "11–25", "25+"],
        "help": "Multiple sites affect AI deployment strategy significantly. On-premise AI at many sites requires network connectivity between them; cloud AI serves all locations from one platform.",
    },
    {
        "id": "site_connectivity",
        "label": "If you have multiple locations, how are they connected?",
        "type": "select",
        "options": [
            "Single location only",
            "Connected via VPN / private WAN",
            "Connected via internet (no private link)",
            "Mostly independent — minimal data sharing between sites",
            "Cloud-first — all sites connect to central cloud services",
        ],
        "help": "Site connectivity is critical for private AI deployments — centralised on-prem AI needs reliable private links between sites. Poor connectivity favours cloud AI or edge-per-site deployment.",
    },
    {
        "id": "current_infra",
        "label": "Current AI / IT infrastructure model",
        "type": "select",
        "options": [
            "Fully on-premises (own servers, no cloud)",
            "Mostly on-premises with some cloud services",
            "Hybrid — balanced mix of on-prem and cloud",
            "Mostly cloud-based",
            "Fully cloud / SaaS — no on-prem servers",
        ],
        "help": "Your existing infrastructure model is the strongest predictor of which AI deployment is practical. On-prem shops can expand to private AI; cloud-first organisations should stay there.",
    },
    {
        "id": "data_sensitivity",
        "label": "What percentage of your business data is sensitive or regulated?",
        "type": "select",
        "options": [
            "< 10% — mostly non-sensitive, public-facing data",
            "10–30% — some internal or customer data",
            "30–60% — significant PII, financial, or operational data",
            "60–80% — most data is sensitive or regulated",
            "> 80% — nearly all data is highly sensitive or regulated",
        ],
        "help": "This is the most important factor in the public vs. private AI decision. Higher sensitivity percentages strongly favour on-prem or hybrid deployments to keep regulated data off third-party cloud.",
    },
    {
        "id": "ai_maturity",
        "label": "Current AI / automation maturity",
        "type": "select",
        "options": [
            "No AI usage at all",
            "Using basic tools (e.g., chatbots, email filters)",
            "Some ML / analytics projects in progress",
            "AI integrated into core workflows",
        ],
        "help": "Current maturity affects how quickly you can adopt new AI. More mature organisations can handle complex deployments; beginners should start with managed cloud AI.",
    },
    {
        "id": "employee_ai_training",
        "label": "Current AI training level of your employees",
        "type": "select",
        "options": [
            "No AI knowledge — staff unfamiliar with AI tools",
            "Basic awareness — some staff have tried consumer AI (ChatGPT etc.)",
            "Moderate — some staff use AI tools in their daily work",
            "Proficient — dedicated team members with AI/ML skills",
            "Advanced — in-house data scientists or ML engineers",
        ],
        "help": "Employee AI readiness shapes both what's feasible and what training investment is needed. Private AI requires significantly higher internal skills than managed cloud AI.",
    },
    {
        "id": "it_team_size",
        "label": "Size of your in-house IT / tech team",
        "type": "select",
        "options": ["None", "1–3", "4–10", "11–25", "25+"],
        "help": "Critical factor — private/hybrid AI requires IT staff to manage servers and models. No IT team strongly favours managed cloud AI.",
    },
    {
        "id": "primary_goals",
        "label": "Primary goals for AI adoption (select all that apply)",
        "type": "multiselect",
        "options": [
            "Cost reduction / operational efficiency",
            "Customer experience improvement",
            "Revenue growth / new products",
            "Risk management / compliance",
            "Employee productivity",
            "Data-driven decision making",
            "Competitive advantage",
        ],
        "help": "Helps prioritise which AI use cases to implement first and which plan best aligns with your strategic objectives.",
    },
    {
        "id": "deployment_pref",
        "label": "Preferred deployment model (if any)",
        "type": "select",
        "options": [
            "No preference — advise me",
            "Prefer cloud / public AI (easier setup)",
            "Prefer on-premise / private AI (data control)",
            "Interested in a hybrid approach",
        ],
        "help": "Your preference is noted but the recommendation is based on all factors. 'Advise me' gives the most unbiased recommendation.",
    },
]

# ═══════════════════════════════════════════════════════════════════════
# INDUSTRY-SPECIFIC QUESTIONS
# ═══════════════════════════════════════════════════════════════════════

INDUSTRY_QUESTIONNAIRES = {

    # ── Manufacturing ─────────────────────────────────────────────────
    "Manufacturing": [
        {
            "id": "mfg_process_type",
            "label": "What type of manufacturing do you primarily do?",
            "type": "select",
            "options": [
                "Discrete (automotive parts, electronics, assembly)",
                "Process (chemicals, food & beverage, pharmaceuticals)",
                "Mixed / hybrid",
                "Job shop / custom fabrication",
                "Additive / 3D printing",
            ],
            "help": "Discrete manufacturing benefits most from defect detection and vision AI. Process manufacturing gains from optimisation and predictive control.",
        },
        {
            "id": "mfg_production_lines",
            "label": "How many active production / assembly lines do you run?",
            "type": "select",
            "options": ["1–3", "4–10", "11–25", "25+"],
            "help": "More lines increase the ROI of AI-driven defect detection and predictive maintenance across your operation.",
        },
        {
            "id": "mfg_ai_use_cases",
            "label": "Which AI use cases interest you? (select all that apply)",
            "type": "multiselect",
            "options": [
                "Predictive maintenance / equipment health monitoring",
                "Quality inspection / defect detection (computer vision)",
                "Demand forecasting & production planning",
                "Supply chain & procurement optimisation",
                "Warehousing & inventory management",
                "Fleet & logistics management",
                "Energy optimisation",
                "Worker safety monitoring",
                "SOP / work instruction generation",
                "Root cause analysis & downtime reduction",
            ],
            "help": "Quality inspection and predictive maintenance require on-premises GPU compute. Forecasting, SOP generation, and fleet management can run in the cloud.",
        },
        {
            "id": "mfg_ot_systems",
            "label": "Do you have connected OT / IoT systems on the factory floor?",
            "type": "radio",
            "options": ["Yes — fully connected with real-time data feeds", "Partially — some machines connected", "No — minimal or no connectivity"],
            "help": "Connected OT/IoT systems are the data foundation for predictive maintenance. Without them, sensor investment is needed before AI can be deployed.",
        },
        {
            "id": "mfg_erp",
            "label": "Which ERP / MES system do you use?",
            "type": "select",
            "options": ["SAP (ECC or S/4HANA)", "Oracle (EBS or Cloud)", "Microsoft Dynamics 365", "Epicor / Infor", "Custom / in-house", "None / spreadsheets"],
            "help": "ERP integration determines how easily AI connects to your production data. SAP and Oracle have established AI connectors.",
        },
        {
            "id": "mfg_downtime_cost",
            "label": "Estimated cost of 1 hour of unplanned production downtime ($)",
            "type": "slider",
            "min": 0,
            "max": 500000,
            "default": 10000,
            "step": 5000,
            "help": "High downtime costs are the strongest justifier for predictive maintenance AI investment and feed directly into your ROI calculation.",
        },
        {
            "id": "mfg_defect_rate",
            "label": "Current defect / scrap rate (approximate)",
            "type": "select",
            "options": [
                "< 1% — very low",
                "1–3% — industry average",
                "3–6% — elevated, room for improvement",
                "> 6% — significant quality issue",
                "Not tracked",
            ],
            "help": "Higher defect rates increase the ROI of AI-powered quality inspection. A 1% reduction in scrap rate at scale often saves hundreds of thousands annually.",
        },
        {
            "id": "mfg_compliance",
            "label": "Which compliance frameworks apply to your operations?",
            "type": "multiselect",
            "options": [
                "ISO 9001 (Quality Management)",
                "ISO 14001 (Environmental)",
                "OSHA / workplace safety",
                "FDA / GMP (food, pharma, medical devices)",
                "FSMA (Food Safety Modernization Act)",
                "ITAR / EAR (export controlled manufacturing)",
                "CMMC / DFARS (defense contracts)",
                "None / general industry standards only",
            ],
            "help": "FDA/GMP, ITAR, and CMMC strongly favour private or hybrid AI — regulated data must not leave your premises. ISO 9001 requires audit-ready AI logs.",
        },
        {
            "id": "mfg_workforce_size",
            "label": "How many shop-floor / production workers do you employ?",
            "type": "select",
            "options": ["< 25", "25–100", "100–500", "500–2,000", "2,000+"],
            "help": "Larger workforces benefit from AI-assisted safety monitoring, training platforms, and SOP generation — all of which have significant per-worker ROI.",
        },
    ],

    # ── Retail & E-Commerce ───────────────────────────────────────────
    "Retail & E-Commerce": [
        {
            "id": "ret_channels",
            "label": "Sales channels you operate",
            "type": "multiselect",
            "options": [
                "Physical stores",
                "Own e-commerce website",
                "Amazon / marketplace",
                "Social commerce (Instagram, TikTok)",
                "Wholesale / B2B",
            ],
            "help": "Multi-channel retailers benefit most from AI-driven inventory sync and personalisation across channels.",
        },
        {
            "id": "ret_ai_use_cases",
            "label": "AI use cases of interest",
            "type": "multiselect",
            "options": [
                "Product recommendations / personalisation",
                "Dynamic pricing",
                "Inventory forecasting & replenishment",
                "Customer service chatbot",
                "Fraud detection",
                "Marketing content generation",
                "Visual search / image recognition",
                "Sentiment analysis / reviews",
            ],
            "help": "Customer-facing AI (chatbots, recommendations) works well with public cloud. Fraud detection with payment data may need private processing.",
        },
        {
            "id": "ret_customer_data",
            "label": "What customer data do you collect?",
            "type": "multiselect",
            "options": [
                "Purchase history",
                "Browsing behaviour",
                "Demographics",
                "Payment information",
                "Loyalty programme data",
                "Location / foot traffic",
            ],
            "help": "Payment data triggers PCI-DSS requirements. More data types give more personalisation power but increase privacy compliance burden.",
        },
        {
            "id": "ret_platform",
            "label": "Primary e-commerce / POS platform",
            "type": "select",
            "options": ["Shopify", "WooCommerce", "Magento", "Square / Toast (POS)", "Custom-built", "Other / None"],
            "help": "Platform choice affects AI integration options. Shopify has built-in AI features; custom platforms offer more flexibility but need more dev work.",
        },
        {
            "id": "ret_sku_count",
            "label": "Approximate number of SKUs",
            "type": "select",
            "options": ["< 100", "100–1,000", "1,000–10,000", "10,000+"],
            "help": "Higher SKU counts benefit more from AI-driven inventory forecasting, dynamic pricing, and recommendation engines.",
        },
        {
            "id": "ret_pci",
            "label": "PCI-DSS compliance status",
            "type": "radio",
            "options": ["Fully compliant", "In progress", "Not compliant / Not sure"],
            "help": "PCI-DSS compliance affects how payment data can be processed by AI systems.",
        },
        {
            "id": "ret_seasonal",
            "label": "How significant are seasonal demand swings for your business?",
            "type": "select",
            "options": [
                "Minimal — fairly flat demand year-round",
                "Moderate — some seasonal peaks (e.g. back to school)",
                "High — major seasonal spikes (e.g. holiday season doubles sales)",
                "Extreme — nearly all revenue in 1-2 months",
            ],
            "help": "High seasonal variability makes demand forecasting AI especially valuable — it enables pre-positioning inventory before peak periods.",
        },
    ],

    # ── Healthcare ────────────────────────────────────────────────────
    "Healthcare": [
        {
            "id": "hc_org_type",
            "label": "Type of healthcare organisation",
            "type": "select",
            "options": [
                "Primary care clinic",
                "Specialty practice",
                "Hospital / health system",
                "Home health / telehealth",
                "Health tech / SaaS",
                "Pharmacy / lab services",
            ],
            "help": "Organisation type determines PHI volume and which AI use cases deliver the highest ROI.",
        },
        {
            "id": "hc_ai_use_cases",
            "label": "AI use cases of interest",
            "type": "multiselect",
            "options": [
                "Clinical documentation / note generation",
                "Patient triage / intake automation",
                "Medical coding / billing",
                "Diagnostic imaging assistance",
                "Drug interaction checks",
                "Appointment scheduling optimisation",
                "Patient engagement / follow-up",
                "Research literature summarisation",
            ],
            "help": "Use cases involving PHI strongly favour private/hybrid. Non-PHI tasks (scheduling, literature) can safely use cloud AI.",
        },
        {
            "id": "hc_ehr",
            "label": "Which EHR system do you use?",
            "type": "select",
            "options": ["Epic", "Cerner (Oracle Health)", "Athenahealth", "Allscripts", "Custom / other", "None"],
            "help": "EHR integration is critical for healthcare AI. Epic and Cerner have robust HL7 FHIR APIs; others may need custom connectors.",
        },
        {
            "id": "hc_hipaa",
            "label": "HIPAA compliance status",
            "type": "radio",
            "options": [
                "Fully compliant with regular audits",
                "Compliant — no recent audit",
                "Working towards compliance",
                "Not applicable",
            ],
            "help": "Any AI touching PHI must be within HIPAA-compliant infrastructure. Non-compliant status means cloud AI cannot be used for clinical data.",
        },
        {
            "id": "hc_phi_volume",
            "label": "Volume of Protected Health Information (PHI) handled daily",
            "type": "select",
            "options": ["Low (< 100 records)", "Moderate (100–1,000)", "High (1,000–10,000)", "Very high (10,000+)"],
            "help": "Higher PHI volume increases both the AI automation ROI and the risk exposure of cloud-based processing.",
        },
        {
            "id": "hc_patient_facing",
            "label": "Will the AI solution be patient-facing?",
            "type": "radio",
            "options": ["Yes", "No — internal / staff only", "Both"],
            "help": "Patient-facing AI has additional requirements for accuracy, liability, and informed consent.",
        },
    ],

    # ── Financial Services ────────────────────────────────────────────
    "Financial Services": [
        {
            "id": "fin_sub_sector",
            "label": "Sub-sector",
            "type": "select",
            "options": [
                "Banking / credit union",
                "Insurance",
                "Wealth management / advisory",
                "Lending / mortgage",
                "Fintech / payments",
                "Accounting / bookkeeping",
            ],
            "help": "Each financial sub-sector has unique regulatory requirements and AI opportunities.",
        },
        {
            "id": "fin_ai_use_cases",
            "label": "AI use cases of interest",
            "type": "multiselect",
            "options": [
                "Fraud detection & AML",
                "Credit risk scoring",
                "Customer onboarding / KYC automation",
                "Document processing (loan apps, claims)",
                "Personalised financial advice",
                "Regulatory reporting automation",
                "Chatbot for customer support",
                "Market analysis / sentiment",
            ],
            "help": "Fraud detection and KYC involve highly sensitive data, favouring private AI. Customer chatbots can often use cloud AI safely.",
        },
        {
            "id": "fin_regulations",
            "label": "Key regulations you must comply with",
            "type": "multiselect",
            "options": ["PCI-DSS", "SOX", "GLBA", "CCPA / state privacy laws", "SEC / FINRA rules", "State insurance regulations", "None specific / unsure"],
            "help": "Each regulation imposes specific data handling requirements that constrain which AI deployment models are viable.",
        },
        {
            "id": "fin_data_residency",
            "label": "Do you have data residency requirements?",
            "type": "radio",
            "options": ["Yes — data must stay in the US", "Yes — data must stay in specific state(s)", "No strict requirements", "Not sure"],
            "help": "Data residency requirements may mandate on-premise processing or restrict which cloud regions can be used.",
        },
        {
            "id": "fin_transaction_volume",
            "label": "Daily transaction volume",
            "type": "select",
            "options": ["< 1,000", "1,000–10,000", "10,000–100,000", "100,000+"],
            "help": "Higher transaction volumes increase cloud AI processing costs but also increase the potential ROI from automation.",
        },
        {
            "id": "fin_audit_trail",
            "label": "How important is AI decision explainability / audit trail?",
            "type": "select",
            "options": ["Nice to have", "Important — internal audits", "Critical — regulatory requirement"],
            "help": "Regulators requiring explainable AI decisions favour platforms that support audit logging and decision transparency.",
        },
    ],

    # ── Telecommunications ────────────────────────────────────────────
    "Telecommunications": [
        {
            "id": "tel_service_type",
            "label": "Primary service type",
            "type": "select",
            "options": [
                "Mobile / wireless",
                "Fixed broadband / ISP",
                "Enterprise networking / SD-WAN",
                "VoIP / UCaaS",
                "Managed services / MSP",
            ],
            "help": "Service type determines data volume, real-time requirements, and highest-value AI use cases.",
        },
        {
            "id": "tel_ai_use_cases",
            "label": "AI use cases of interest",
            "type": "multiselect",
            "options": [
                "Network anomaly detection",
                "Customer churn prediction",
                "Call centre / support automation",
                "Capacity planning",
                "Billing optimisation",
                "Proactive outage management",
                "Personalised plan recommendations",
                "Technician dispatch optimisation",
            ],
            "help": "Network AI needs real-time low-latency processing (favours private/edge). Customer-facing chatbots work well with cloud AI.",
        },
        {
            "id": "tel_subscriber_base",
            "label": "Approximate subscriber / customer base",
            "type": "select",
            "options": ["< 1,000", "1,000–10,000", "10,000–100,000", "100,000+"],
            "help": "Larger subscriber bases increase data volumes and AI costs but also increase ROI from churn reduction and support automation.",
        },
        {
            "id": "tel_network_data",
            "label": "Do you have access to network telemetry / CDR data?",
            "type": "radio",
            "options": ["Yes — real-time", "Yes — batch / historical", "No"],
            "help": "Network telemetry enables predictive maintenance and anomaly detection. Without it, additional data infrastructure is needed.",
        },
        {
            "id": "tel_cpni",
            "label": "CPNI (Customer Proprietary Network Information) handling",
            "type": "select",
            "options": ["Strict controls in place", "Basic controls", "Needs improvement", "Not sure what CPNI is"],
            "help": "CPNI regulations restrict how customer network data can be used and shared, directly impacting whether cloud AI can process it.",
        },
        {
            "id": "tel_legacy",
            "label": "How much legacy infrastructure do you still operate?",
            "type": "select",
            "options": ["Minimal — mostly cloud-native", "Moderate — mix of legacy and modern", "Significant — major legacy systems"],
            "help": "Heavy legacy infrastructure may complicate AI integration and favour cloud-based solutions that don't require deep on-prem integration.",
        },
    ],

    # ── Logistics & Supply Chain ──────────────────────────────────────
    "Logistics & Supply Chain": [
        {
            "id": "log_segment",
            "label": "Primary logistics segment",
            "type": "select",
            "options": [
                "Freight / trucking",
                "Warehousing & distribution",
                "Last-mile delivery",
                "3PL / 4PL provider",
                "Freight brokerage",
                "Cold chain / perishables",
            ],
            "help": "Each logistics segment has different data types, real-time requirements, and AI opportunities.",
        },
        {
            "id": "log_ai_use_cases",
            "label": "AI use cases of interest",
            "type": "multiselect",
            "options": [
                "Route optimisation",
                "Demand forecasting",
                "Warehouse automation / pick optimisation",
                "Shipment tracking & ETA prediction",
                "Carrier selection / rate negotiation",
                "Document processing (BOL, invoices)",
                "Fleet maintenance prediction",
                "Returns / reverse logistics",
            ],
            "help": "Route optimisation and ETA prediction need real-time compute. Document processing and forecasting can run as batch jobs.",
        },
        {
            "id": "log_fleet_size",
            "label": "Approximate fleet / vehicle count (if applicable)",
            "type": "select",
            "options": ["No fleet", "1–10 vehicles", "11–50 vehicles", "51–200 vehicles", "200+ vehicles"],
            "help": "Larger fleets have greater ROI from AI-driven route optimisation and predictive maintenance — fuel and maintenance savings multiply with fleet size.",
        },
        {
            "id": "log_tms",
            "label": "TMS / WMS system in use",
            "type": "select",
            "options": ["SAP TM / EWM", "Oracle TMS", "Blue Yonder", "Manhattan Associates", "Custom / spreadsheets", "None"],
            "help": "Your TMS/WMS integration capabilities affect how AI connects to operations. Enterprise systems have APIs; spreadsheet-based workflows need more custom work.",
        },
        {
            "id": "log_shipment_volume",
            "label": "Monthly shipment volume",
            "type": "select",
            "options": ["< 500", "500–5,000", "5,000–50,000", "50,000+"],
            "help": "Higher shipment volumes increase AI processing costs but also increase the savings from optimisation.",
        },
        {
            "id": "log_real_time",
            "label": "Do you have real-time GPS / IoT tracking on shipments?",
            "type": "radio",
            "options": ["Yes", "Partial", "No"],
            "help": "Real-time tracking enables predictive ETA and proactive exception management. Without it, AI is limited to historical analysis.",
        },
        {
            "id": "log_cold_chain",
            "label": "Do you operate cold chain / temperature-controlled shipments?",
            "type": "radio",
            "options": ["Yes — primary business", "Yes — partial / some shipments", "No"],
            "help": "Cold chain operations have strict compliance requirements for temperature logging and breach response that AI monitoring must support.",
        },
    ],
}
