"""
sponsor_classifier.py — SAFE Evidence Lab, shared across all Methodology C topics.
====================================================================================
Classifies a trial's LEAD SPONSOR into (is_industry, category) from the free-text
sponsor name plus ClinicalTrials.gov's coarse LeadSponsorClass field.

Design:
  * Built once, shared by every condition (Pfizer sponsors trials in many diseases).
  * Precedence is deliberate: strong NON-industry institutional signals are tested
    before generic industry suffixes, so "National Cancer Institute" is never called
    industry, while "Genentech, Inc." still is.
  * The goal is a near-empty residual so no human review of thousands of "OTHER" rows
    is needed. classify_frame() reports the residual so you can confirm.

Categories: industry, academic, hospital, government, research_nonprofit, network,
individual, other.  is_industry is the boolean used in the primary analysis
(industry vs non-industry, matching the DeVito 2020 split).
"""
import re

# --- major pharma / biotech / device companies (catch names lacking a legal suffix) ---
COMPANIES = [
    "pfizer","novartis","roche","genentech","merck","msd","schering-plough","glaxosmithkline","glaxo",
    "gsk","astrazeneca","zeneca","sanofi","aventis","genzyme","bayer","boehringer ingelheim","boehringer",
    "bristol-myers squibb","bristol myers squibb","bms","eli lilly","lilly","johnson & johnson","janssen",
    "abbvie","abbott","amgen","gilead","kite pharma","biogen","idec","takeda","shire","baxalta","astellas",
    "daiichi sankyo","daiichi","eisai","otsuka","teva","mylan","viatris","sandoz","hexal","novo nordisk",
    "regeneron","vertex","moderna","biontech","curevac","servier","ucb","grunenthal","grünenthal","chiesi",
    "ipsen","lundbeck","alexion","incyte","jazz pharmaceuticals","alkermes","fresenius","kabi","celgene",
    "seagen","seattle genetics","bluebird bio","alnylam","ionis","sarepta","beigene","hutchmed","legend biotech",
    "genmab","argenx","galapagos","morphosys","evotec","zealand pharma","ascendis","y-mabs","exelixis",
    "arena pharmaceuticals","reata","mirati","turning point","blueprint medicines","deciphera","epizyme",
    "karuna","cerevel","sage therapeutics","axsome","intra-cellular","neurocrine","supernus","acadia",
    "corcept","horizon therapeutics","amarin","esperion","the medicines company","cytokinetics","myokardia",
    "boston scientific","medtronic","stryker","edwards lifesciences","becton dickinson","becton, dickinson",
    "siemens healthineers","siemens","philips","ge healthcare","zimmer biomet","zimmer","smith & nephew",
    "intuitive surgical","cook medical","cook incorporated","terumo","b. braun","braun melsungen","olympus",
    "insulet","dexcom","tandem diabetes","bausch","valeant","alcon","allergan","coloplast","convatec","hologic",
    "illumina","thermo fisher","qiagen","biomerieux","biomérieux","hoffmann-la roche","f. hoffmann","csl behring",
    "csl","grifols","octapharma","kedrion","emergent biosolutions","dynavax","valneva","novavax","sinovac",
    "sinopharm","cansino","serum institute","bharat biotech","dr. reddy","sun pharma","cipla","lupin","zydus",
    "hikma","aurobindo","glenmark","torrent pharma","intas","biocon","celltrion","samsung bioepis","lg chem",
    "hanmi","yuhan","chong kun dang","green cross","kyowa kirin","kyowa hakko","mitsubishi tanabe","shionogi",
    "ono pharmaceutical","sumitomo","dainippon","kissei","nippon shinyaku","taisho","tsumura","meiji seika",
    "menarini","recordati","angelini","alfasigma","zambon","dompé","dompe","almirall","ferrer","esteve",
    "pierre fabre","les laboratoires servier","stallergenes","vifor","galderma","leo pharma","orion pharma",
    "santhera","idorsia","actelion","basilea","polyphor","addex","newron","cosmo pharmaceuticals",
]
COMPANY_RE = re.compile(r"\b(" + "|".join(re.escape(c) for c in COMPANIES) + r")\b", re.I)

# --- corporate / legal-entity suffixes (multilingual) => industry ---
CORP_SUFFIX = re.compile(
    r"(\b(inc|incorporated|corp|corporation|co|company|holdings?)\b\.?|"
    r"\b(ltd|limited|llc|l\.l\.c|llp|plc|pty|inc)\b\.?|"
    r"\b(gmbh|ag|kg|kgaa|mbh|se)\b|"
    r"\b(s\.?a\.?|s\.?a\.?s|s\.?p\.?a|spa|s\.?r\.?l|srl|s\.?l|n\.?v|b\.?v|bvba|oy|oyj|ab|a/s|aps|as|sarl|sas)\b|"
    r"\b(k\.?k|co\.?,?\s*ltd|pvt\.?\s*ltd|sdn\.?\s*bhd|pte\.?\s*ltd)\b)", re.I)

# --- industry-signal words (weaker; used only if not already non-industry) ---
INDUSTRY_WORDS = re.compile(
    r"\b(pharmaceutical|pharmaceutica|pharma|biopharma|biopharmaceutical|biosciences?|bioscience|"
    r"biotech|biotechnolog\w*|therapeutic|therapeutics|biologics?|medicines?|medical systems|"
    r"medtech|drug delivery|vaccines?|genomics?|molecular|nanotech\w*|"
    r"laboratoires|laboratories|labs)\b", re.I)

# --- GOVERNMENT signals ---
GOVERNMENT = re.compile(
    r"\b(national institute|national institutes|nih\b|nci\b|nhlbi|niaid|nimh|niddk|ninds|"
    r"national cancer institute|national heart|centers for disease control|\bcdc\b|"
    r"food and drug administration|\bfda\b|veterans affairs|\bva\b medical|va health|"
    r"walter reed|army|navy|air force|department of defense|\bdod\b|military|armed forces|"
    r"ministry|ministerio|minist[eè]re|ministero|department of health|public health|health canada|"
    r"instituto nacional|institut national|inserm|\bcnrs\b|\bcnr\b|\bcsic\b|conicet|"
    r"assistance publique|\bap-?hp\b|bundes\w*|helmholtz|max planck|fraunhofer|"
    r"national health service|\bnhs\b|korea disease control|agenzia italiana|\baifa\b|"
    r"medical research council|\bmrc\b|federal|government|govern\w*|state of|county of|"
    r"institut pasteur|robert koch)\b", re.I)

# --- ACADEMIC (university/college/school) ---
ACADEMIC = re.compile(
    r"\b(universit\w*|college|school of medicine|faculty of medicine|medical school|"
    r"[ée]cole|escuela|hochschule|polytechnic|institute of technology|institutet|"
    r"karolinska|\buniv\b\.?)\b", re.I)

# --- HOSPITAL / clinical center ---
HOSPITAL = re.compile(
    r"\b(hospital|h[oô]pital|hospitalier|ospedale|krankenhaus|klinik\w*|clinic|cl[ií]nica|"
    r"medical cent(er|re)|health cent(er|re)|health system|health network|infirmary|"
    r"cancer cent(er|re)|comprehensive cancer|\bchu\b|\bchr\b|mayo clinic|cleveland clinic|"
    r"kaiser|charit[ée]|mount sinai|massachusetts general|brigham|cedars-?sinai|"
    r"memorial sloan|md anderson|dana-?farber|fred hutchinson|sunnybrook|"
    r"\btrust\b.*\bnhs\b|nhs\b.*\btrust\b|hospices civils)\b", re.I)

# --- RESEARCH NONPROFIT / foundations / cooperative groups ---
NONPROFIT = re.compile(
    r"\b(institut\w*|instituto|istituto|research (cent(er|re)|foundation|institute|network)|"
    r"foundation|fondation|fondazione|fundaci[oó]n|stiftung|charitable|charity|wellcome|"
    r"gates foundation|\beortc\b|\bswog\b|\becog\b|ecog-?acrin|\bnrg\b|children'?s oncology|"
    r"\brtog\b|\bgog\b|\bnsabp\b|\bcalgb\b|\bibcsg\b|breast international group|\bgbg\b|"
    r"cooperative group|consortium|collaborative|\balliance\b|society|association|"
    r"registry|academic and community|"
    r"(breast|cancer|oncology|leukemia|leukaemia|lymphoma|myeloma|melanoma|sarcoma|tumou?r|"
    r"study|trials?|research|working|cooperative|collaborative|clinical trials?) group)\b", re.I)

NETWORK_WORDS = re.compile(r"\b(network|cooperative group|consortium|study group|trial group)\b", re.I)


def classify_sponsor(name, ctgov_class=None):
    """Return (is_industry: bool, category: str)."""
    cls = str(ctgov_class or "").upper()
    nm = str(name or "").strip()

    # 1) trust CT.gov's own coarse buckets where they are reliable
    if cls == "INDUSTRY":
        return True, "industry"
    if cls in ("NIH", "FED", "OTHER_GOV"):
        return False, "government"
    if cls == "NETWORK":
        return False, "network"
    if cls == "INDIV":
        return False, "individual"

    # 2) class is OTHER / UNKNOWN / missing -> refine from the NAME.
    #    Non-industry institutional signals FIRST so they win ties.
    if not nm:
        return False, "other"
    if GOVERNMENT.search(nm):   return False, "government"
    if ACADEMIC.search(nm):     return False, "academic"
    if HOSPITAL.search(nm):     return False, "hospital"
    if NONPROFIT.search(nm):
        return False, ("network" if NETWORK_WORDS.search(nm) else "research_nonprofit")

    # 3) industry signals: a named company, a legal suffix, or a pharma keyword
    if COMPANY_RE.search(nm) or CORP_SUFFIX.search(nm) or INDUSTRY_WORDS.search(nm):
        return True, "industry"

    # 4) genuinely unresolved
    return False, "other"


def classify_frame(df, name_col="lead_sponsor_name", class_col="sponsor_class"):
    """Adds sponsor_industry (bool) and sponsor_category (str). Returns (df, residual_report)."""
    names = df[name_col] if name_col in df.columns else [None] * len(df)
    classes = df[class_col] if class_col in df.columns else [None] * len(df)
    ind, cat = [], []
    for n, c in zip(names, classes):
        i, k = classify_sponsor(n, c)
        ind.append(i); cat.append(k)
    df = df.copy()
    df["sponsor_industry"] = ind
    df["sponsor_category"] = cat
    n = len(df)
    resid = int((df["sponsor_category"] == "other").sum())
    report = {"n": n, "residual_other": resid,
              "residual_pct": round(100 * resid / n, 1) if n else 0.0,
              "distribution": df["sponsor_category"].value_counts().to_dict()}
    return df, report


# =====================================================================================
# CDQI EXTENSION (exploratory sub-category refinement) — appended; ALL original code above
# is left intact. This block ONLY refines names the base classifier leaves as "other" into
# non-industry sub-categories. It NEVER changes is_industry: every path here is non-industry,
# so the primary industry-vs-non-industry split is frozen by construction and identical to the
# base classifier. Only the descriptive sub-categories get sharper. Applied because the base
# instrument was built for oncology names and leaves a large residual on CDQI's surgical/pain/
# anesthesia topics (individual investigators, non-English health systems, regional public
# health bodies, multilingual cooperative groups). Documented as an extension of the pre-
# specified instrument; the residual is re-reported after refinement.
# =====================================================================================

_EXT_PRIVATE   = re.compile(r"\b(pllc|p\.?l\.?l\.?c|ramsay|elsan)\b|treatment cent(er|re)", re.I)
_EXT_COOP      = re.compile(r"\b(unicancer|gortec|cancer research uk)\b|groupe oncolog\w*|"
                            r"gruppo oncologico|grupo espa[nñ]ol|groupe d'?[eé]tude", re.I)
_EXT_ACADEMIC  = re.compile(r"\b(universidad|universit[àá]|universidade|pontificia|academ\w*)\b", re.I)
_EXT_GOVREGION = re.compile(r"\bregion\b|health authority|regional health", re.I)
_EXT_HOSPITAL  = re.compile(r"health|hospit\w*|klinik\w*|\bumc\b|\bamc\b|herzzentrum|campus|"
                            r"ciusss|cisss|medical organization|infirm\w*|cent(er|re)|\bkrankenhaus\b", re.I)

def _looks_like_person(nm):
    """A bare 2-3 token human name with no digits and no institutional signal (base already
    ruled out companies/suffixes/keywords before returning 'other')."""
    s = re.sub(r"^(dr|prof|professor|mr|ms|mrs|md)\.?\s+", "", nm.strip(), flags=re.I)
    if any(ch.isdigit() for ch in s):
        return False
    toks = s.split()
    if not (2 <= len(toks) <= 3):
        return False
    _INST_LEAD = {"centre","center","az","asst","institut","institute","division","unit",
                  "department","service","groupe","groep","hospital","clinic","cancer"}
    if toks[0].lower().strip(".,") in _INST_LEAD:
        return False
    for t in toks:
        if len(t) >= 2 and t.isupper():   # acronym like AZ / ASST / CTO -> not a person
            return False
        if re.fullmatch(r"[A-Z]\.", t):        # middle initial like "J."
            continue
        if not re.fullmatch(r"[A-ZÀ-Ý][\wÀ-ÿ'’.-]+", t):
            return False
    return True

def _refine_other(name):
    nm = str(name or "").strip()
    if not nm:
        return "other"
    if _EXT_PRIVATE.search(nm):    return "private_practice"     # non-industry, own bucket
    if _EXT_COOP.search(nm):       return "research_nonprofit"
    if _EXT_ACADEMIC.search(nm):   return "academic"
    if _EXT_GOVREGION.search(nm):  return "government"
    if _EXT_HOSPITAL.search(nm):   return "hospital"
    if _looks_like_person(nm):     return "individual"
    return "other"

# ---- override the module-level classify_frame so importers pick up the CDQI-extended version.
#      The base classify_frame remains defined above (shadowed) for audit; is_industry still
#      comes wholly from the base classify_sponsor and is never modified here.
def classify_frame(df, name_col="lead_sponsor_name", class_col="sponsor_class"):
    names   = df[name_col]  if name_col  in df.columns else [None]*len(df)
    classes = df[class_col] if class_col in df.columns else [None]*len(df)
    ind, cat = [], []
    for n, c in zip(names, classes):
        i, k = classify_sponsor(n, c)          # base: authoritative for is_industry
        if k == "other":
            k = _refine_other(n)               # refine sub-category ONLY (still non-industry)
        ind.append(i); cat.append(k)
    df = df.copy()
    df["sponsor_industry"] = ind
    df["sponsor_category"] = cat
    n = len(df)
    resid = int((df["sponsor_category"] == "other").sum())
    report = {"n": n, "residual_other": resid,
              "residual_pct": round(100*resid/n, 1) if n else 0.0,
              "distribution": df["sponsor_category"].value_counts().to_dict()}
    return df, report


if __name__ == "__main__":
    # self-test against a representative set of REAL sponsor names spanning every bucket
    import pandas as pd
    tests = [
        # industry (with and without suffix)
        ("Pfizer", None), ("Genentech, Inc.", "OTHER"), ("Boehringer Ingelheim", "INDUSTRY"),
        ("Novartis Pharmaceuticals", "OTHER"), ("AstraZeneca", None), ("Regeneron Pharmaceuticals",  "OTHER"),
        ("Vertex Pharmaceuticals Incorporated", "OTHER"), ("Chiesi Farmaceutici S.p.A.", "OTHER"),
        ("Grünenthal GmbH", "OTHER"), ("Daiichi Sankyo Co., Ltd.", "OTHER"), ("Teva Branded Pharmaceutical", "OTHER"),
        ("Acme Therapeutics", "OTHER"), ("Novo Nordisk A/S", "OTHER"), ("Medtronic", "OTHER"),
        ("Boston Scientific Corporation", "OTHER"), ("Insulet Corporation", "OTHER"),
        # academic
        ("University of Oxford", "OTHER"), ("Universität Heidelberg", "OTHER"),
        ("Johns Hopkins University", "OTHER"), ("Université de Montréal", "OTHER"),
        ("Imperial College London", "OTHER"), ("Karolinska Institutet", "OTHER"),
        # hospital
        ("Massachusetts General Hospital", "OTHER"), ("Cleveland Clinic", "OTHER"),
        ("Assistance Publique - Hôpitaux de Paris", "OTHER"), ("Charité - Universitätsmedizin Berlin", "OTHER"),
        ("MD Anderson Cancer Center", "OTHER"), ("Ospedale San Raffaele", "OTHER"),
        # government
        ("National Cancer Institute (NCI)", "NIH"), ("National Heart, Lung, and Blood Institute", "NIH"),
        ("INSERM", "OTHER"), ("Ministry of Health, Israel", "OTHER"),
        ("US Department of Veterans Affairs", "FED"), ("Instituto Nacional de Cancerología", "OTHER"),
        # nonprofit / cooperative groups
        ("EORTC", "OTHER"), ("SWOG Cancer Research Network", "NETWORK"),
        ("Bill & Melinda Gates Foundation", "OTHER"), ("Breast International Group", "OTHER"),
        ("German Breast Group", "OTHER"),
        # individual / edge
        ("Dr. Jane Smith", "INDIV"), ("", "UNKNOWN"),
    ]
    dft = pd.DataFrame(tests, columns=["lead_sponsor_name", "sponsor_class"])
    dft, rep = classify_frame(dft)
    for _, r in dft.iterrows():
        print(f"  {r['sponsor_industry']!s:5}  {r['sponsor_category']:18} | {r['lead_sponsor_name']}")
    print("\nresidual 'other':", rep["residual_other"], f"/{rep['n']}", f"({rep['residual_pct']}%)")
    print("distribution:", rep["distribution"])
