'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''


###################################################### LINKEDIN SEARCH PREFERENCES ######################################################

# These Sentences are Searched in LinkedIn
# Enter your search terms inside '[ ]' with quotes ' "searching title" ' for each search followed by comma ', ' Eg: ["Software Engineer", "Software Developer", "Selenium Developer"]
search_terms = [
    # Scientific ML / materials AI
    "Scientific Machine Learning",
    "Physics Informed Machine Learning",
    "Materials Informatics Scientist",
    "Computational Materials Scientist",
    "Machine Learning Scientist Materials",
    "Surrogate Modeling Engineer",
    "Simulation Machine Learning Engineer",
    "CAE Machine Learning Engineer",
    "Computational Mechanics Engineer",
    "Digital Twin Modeling Engineer",

    # Battery / thermal / reliability
    "Battery Thermal Modeling Engineer",
    "Battery Modeling Engineer",
    "Battery Reliability Engineer",
    "Battery Data Scientist",
    "Thermal Systems Simulation Engineer",
    "Energy Storage Machine Learning",

    # Manufacturing / industrial AI
    "Manufacturing Machine Learning Engineer",
    "Industrial AI Engineer",
    "Smart Manufacturing Data Scientist",
    "Process Quality Data Scientist",
    "Sensor Fusion Machine Learning Engineer",
    "Predictive Maintenance Machine Learning",

    # Corrosion / materials characterization
    "Materials Modeling Engineer",
    "Corrosion Modeling Engineer",
    "Degradation Modeling Engineer",
    "Reliability Modeling Engineer",
    "Materials Characterization Scientist",
    "Microscopy Data Scientist",

    # Secondary computer vision route
    "Computer Vision Engineer Manufacturing",
    "Computer Vision Engineer Materials",
    "Perception Machine Learning Engineer",
    "Imaging Machine Learning Scientist",
]

# Search location, this will be filled in "City, state, or zip code" search box. If left empty as "", tool will not fill it.
search_location = "United States"               # Some valid examples: "", "United States", "India", "Chicago, Illinois, United States", "90001, Los Angeles, California, United States", "Bengaluru, Karnataka, India", etc.

# After how many number of applications in current search should the bot switch to next search? 
switch_number = 20                 # Only numbers greater than 0... Don't put in quotes

# Do you want to randomize the search order for search_terms?
randomize_search_order = False     # True of False, Note: True or False are case-sensitive


# >>>>>>>>>>> Job Search Filters <<<<<<<<<<<
sort_by = "Most recent"                       # "Most recent", "Most relevant" or ("" to not select) 
date_posted = "Past week"         # "Any time", "Past month", "Past week", "Past 24 hours" or ("" to not select)
salary = ""                        # "$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+"

easy_apply_only = True             # True or False, Note: True or False are case-sensitive

experience_level = ["Entry level", "Associate", "Mid-Senior level"]              # (multiple select) "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"
job_type = ["Full-time"]                      # (multiple select) "Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"
on_site = ["On-site", "Remote", "Hybrid"]                       # (multiple select) "On-site", "Remote", "Hybrid"

companies = []                     # (dynamic multiple select) 
location = []                      # (dynamic multiple select)
industry = []                      # (dynamic multiple select)
job_function = []                  # (dynamic multiple select)
job_titles = []                    # (dynamic multiple select)
benefits = []                      # (dynamic multiple select)
commitments = []                   # (dynamic multiple select)

under_10_applicants = False        # True or False, Note: True or False are case-sensitive
in_your_network = False            # True or False, Note: True or False are case-sensitive
fair_chance_employer = False       # True or False, Note: True or False are case-sensitive


## >>>>>>>>>>> RELATED SETTING <<<<<<<<<<<

# Pause after applying filters to let you modify the search results and filters?
pause_after_filters = True         # True or False, Note: True or False are case-sensitive

##




## >>>>>>>>>>> SKIP IRRELEVANT JOBS <<<<<<<<<<<
 
# Avoid applying to these companies, and companies with these bad words in their 'About Company' section...
about_company_bad_words = ["Crossover", "Staffing", "Recruiting"]       # (dynamic multiple search) or leave empty as []. Ex: ["Staffing", "Recruiting", "Name of Company you don't want to apply to"]

# Skip checking for `about_company_bad_words` for these companies if they have these good words in their 'About Company' section... [Exceptions, For example, I want to apply to "Robert Half" although it's a staffing company]
about_company_good_words = []      # (dynamic multiple search) or leave empty as []. Ex: ["Robert Half", "Dice"]

# Avoid applying to these companies if they have these bad words in their 'Job Description' section...  (In development)
bad_words = [
    "US Citizen",
    "USA Citizen",
    "U.S. Citizen",
    "US Citizenship",
    "U.S. Citizenship",
    "Security Clearance",
    "Active Clearance",
    "Top Secret",
    "No C2C",
    "No Corp2Corp",
    ".NET",
    "PHP",
    "Ruby",
    "CNC",
    "Frontend",
    "Front End",
    "React Developer",
    "Node.js Developer",
    "Web Developer",
    "Sales",
    "Recruiter",
]

# Do you have an active Security Clearance? (True for Yes and False for No)
security_clearance = False         # True or False, Note: True or False are case-sensitive

# Do you have a Masters degree? (True for Yes and False for No). If True, the tool will apply to jobs containing the word 'master' in their job description and if it's experience required <= current_experience + 2 and current_experience is not set as -1. 
did_masters = True                 # True or False, Note: True or False are case-sensitive

# Avoid applying to jobs if their required experience is above your current_experience. (Set value as -1 if you want to apply to all ignoring their required experience...)
current_experience = 5             # Integers > -2 (Ex: -1, 0, 1, 2, 3, 4...)
##






############################################################################################################
try:
    from modules.user_profile import apply_section
    apply_section(globals(), "search")
except Exception:
    pass
'''
THANK YOU for using my tool 😊! Wishing you the best in your job hunt 🙌🏻!

Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. Your support keeps this project alive.

Support my work on <PATREON_LINK>. Together, we can help more job seekers.

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact.

Your support, whether through donations big or small or simply spreading the word, means the world to me and helps keep this project alive and thriving.

Gratefully yours 🙏🏻,
Sai Vignesh Golla
'''
############################################################################################################
