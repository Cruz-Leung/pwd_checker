import gooeypie as gp
import re
from pwd_database import breached_pwd_list
from sequential_database import sequential_patterns

app = gp.GooeyPieApp("Password Checker")
app.width = 1200
app.height = 750
app.set_grid(7, 3)


def toggle_pwd_visibility(event):
    password_input.toggle()

def progress_bar_update(score):
    max_score = 7
    percent = int((score / max_score) * 100)
    progress_bar.value = max(0, min(percent, 100))
    
### Update password length label and check password strength
def update_pwd_length(event):
    pwd = password_input.text

    # Check if the password is empty
    if pwd == "":
        pwd_len_lbl.text = "Length: 0 characters"
        status_lbl.text = "No Password"
        status_lbl.color = "#FFFFFF"
        display_critical.text = ""
        display_weakness.text = ""
        display_suggestion.text = "" 
        breach_lbl.text = "Breach Status: Unknown"
        breach_lbl.color = "#FFFFFF"
        breach_message.text = ""

        return 0
    else:
        pwd_len_lbl.text = f"Length: {len(pwd)} characters"
        
    check_password(event)  

### CHECK FOR COMMON PASSWORD REQUIREMENTS
def check_password(event): # check password strength
    pwd = password_input.text
    score = 0
    progress_bar.value = 0
    required_components = []
    weakness_feedback = []
    feedback = []
    major_weakness_count = 0
    requirement_fail = False
    breached_fail = False
    breach_count = 0

    
    
    # length check
    if len(pwd)>= 12:
        score += 3
    elif len(pwd)>= 10:
        score += 2
        feedback.append("- Consider using more characters")
    elif len(pwd) >= 8:
        score += 1
        feedback.append("- Consider using more characters")
    elif len(pwd) >= 6:
        weakness_feedback.append("- Include 8 characters")
        major_weakness_count += 1
    else:
        required_components.append("- Include 8 characters")
        requirement_fail = True
    
    ## Basic character checks
   # letter check
    if any(char.isdigit() for char in pwd):
        score += 1
    else:
        weakness_feedback.append("- Include one number")
        major_weakness_count += 1

    # Upper case check
    if any(char.isupper() for char in pwd):
        score += 1
    else:
        weakness_feedback.append("- Include one uppercase letter")
        major_weakness_count += 1

    # Lower case check
    if any(char.islower() for char in pwd):
        score += 1
    else:
        weakness_feedback.append("- Include one lowercase letter")
        major_weakness_count += 1

    # Special character check
    if any(char in "!@#$%^&*()_+-=[]{}|;:',.<>/?`~" for char in pwd):
        score += 1
    else:
        feedback.append("- Include one special character")

    ### List of password checks performed
    requirement_fail, required_components = check_common_pwds(pwd, requirement_fail, required_components) 
    requirement_fail, required_components = check_dictionary_words(pwd, requirement_fail, required_components)
    breached_fail, breach_count = breached_password_check(event, pwd, breached_fail, breach_count)
    major_weakness_count, weakness_feedback = repeated_pattern_check(event, pwd, major_weakness_count, weakness_feedback)
   

    ### Calculate final score
    if requirement_fail == True:
        score = 0
    score -= min(major_weakness_count, 4) # limit weakness penalty to maximum 3 points
    score = max(score, 0)  # Ensure score is not negative
    if breached_fail == True:
        score = 0
        breach_lbl.text = "Breach Status: Breached"
        breach_lbl.color = "#ff0000"
        breach_message.text = f"Password has appeared in known data breaches {breach_count} times" 
    else: 
        breach_lbl.text = "Breach Status: Not Breached"
        breach_lbl.color = "#48ff00"
        breach_message.text = "Password not found in known data breaches."

    # Update status label
    strength_status(event, score)
        
    # run progress bar 
    progress_bar_update(score)

   
    # display feedback 
    if required_components == []:
        display_critical.text = "No required components missing"
    else: 
        display_critical.text = "\n".join(required_components)

    if weakness_feedback == []:
        display_weakness.text = "No major weakness"
    else: 
        display_weakness.text = "\n".join(weakness_feedback)

    if feedback == []:
        display_suggestion.text = "No suggestions"
    else: 
        display_suggestion.text = "\n".join(feedback)


### CHECK FOR COMMON PASSWORDS
def check_common_pwds(pwd, requirement_fail, required_components):
    lower_pwd = pwd.lower()

    f = open("/Users/cruzleung/Desktop/school/SEN/11SEN/assessment_2/pwd_checker/txt_files/common_pwdlist.txt") # Stored in file "txt_files"
    common_passwords = f.readlines()
    cleaned_common_pwd = []

    for password in common_passwords: 
        password = password.replace("\n", "")
        cleaned_common_pwd.append(password)

    if pwd in cleaned_common_pwd or lower_pwd in cleaned_common_pwd:
        requirement_fail = True
        required_components.append("- Found in top passwords" + "\n  Choose something more unique")
    
    return requirement_fail, required_components
        

### CHECK FOR DICTIONARY WORDS
def check_dictionary_words(pwd, requirement_fail, required_components):
    lower_pwd = pwd.lower()

    f = open("/Users/cruzleung/Desktop/school/SEN/11SEN/assessment_2/pwd_checker/txt_files/words_alpha.txt")
    dictionary_words = f.readlines()
    cleaned_dictionary_words = []

    for word in dictionary_words:
        word = word.replace("\n", "")
        cleaned_dictionary_words.append(word)

    if pwd in cleaned_dictionary_words or lower_pwd in cleaned_dictionary_words:
        requirement_fail = True
        required_components.append("- Found in dictionary words" + "\n  Choose something more unique")
    
    return requirement_fail, required_components

### CHECK FOR BREACHED PASSWORDS
def breached_password_check(event, pwd, breached_fail, breach_count):
    lower_pwd = pwd.lower()

    # Check if the password is in the breached password list
    for entry in breached_pwd_list:
        if entry['password'] == lower_pwd or entry['password'] == pwd:
            breached_fail = True
            breach_count = int(entry['count'])
            return breached_fail, breach_count  # Return immediately if found
    return False, 0  # Return if not found in the list
    
### REPEATED CHARACTER AND PATTERN CHECK
### Looked up python module re for regular expressions with some AI assistant and self editing to suit code
def repeated_pattern_check(event, pwd, major_weakness_count, weakness_feedback):
    lower_pwd = pwd.lower()
    
    # Check for repeated character 
    # i.e. "aaa", "1111", "zzzzzz"
    if re.search(r'(.)\1{2,}', lower_pwd): 
        major_weakness_count += 2
        weakness_feedback.append("- Avoid repeating the same character")

    # Check for repeated patterns
    # i.e. "abab", "123123", "xyzxyz", "abcabcabc"
    # Check for repeated substrings (like "abcabcabc")
    if re.search(r'(.+?)\1{1,}', lower_pwd):
    ## Code explaination: (.+?) captures any sequence of 1 or more characters ## \1{2,} looks for it to repeat at least 2 more times consecutively
        major_weakness_count += 2
        weakness_feedback.append("- Repeated sequence detected")

    # Low diversity check, 1-3 unique characters
    if len(set(pwd)) <= 3 and len(pwd) >= 6:  
        major_weakness_count += 2
        weakness_feedback.append("- Too few unique characters in the password")

    # sequential patterns check
    sequential_pattern = 0
    for pattern in sequential_patterns:
        if pattern in lower_pwd:
            sequential_pattern += 1
            weakness_feedback.append(f"- Sequential patterns '{pattern}' detected")

    if sequential_pattern > 0:
        major_weakness_count += max(sequential_pattern, 3)

    return major_weakness_count, weakness_feedback
    


def strength_status(event, score):
    if score == 7: 
        status_lbl.text = "Very Strong"
        status_lbl.color = "#48ff00"
    elif score == 6: 
        status_lbl.text = "Strong"
        status_lbl.color = "#b9e320"
    elif score == 5:
        status_lbl.text = "Mediocre"
        status_lbl.color = "#ddeb1a"
    elif score > 3:
        status_lbl.text = "Weak"
        status_lbl.color = "#ff9100"
    elif score > 1: 
        status_lbl.text = "Very Weak"
        status_lbl.color = "#ff0000"
    elif score >= 0:
        status_lbl.text = "Never use this password"
        status_lbl.color = "#ff0000"
        

# labels 

# logo 
logo = gp.Image(app, "/Users/cruzleung/Desktop/school/SEN/11SEN/assessment_2/pwd_checker/images/logo.png")

### Test Label
heading_label = gp.StyleLabel(app, 'Password Strengthener')
heading_label.font_name = 'Noto Sans Myanmar'
heading_label.font_size = 32
heading_label.font_weight = 'bold'

password_lbl = gp.Label(app, "Password")

password_input = gp.Secret(app)
password_input.justify = 'left'
password_input.width = 50
show_pwd = gp.Checkbox(app, "Show Password")
show_pwd.add_event_listener("change", toggle_pwd_visibility)

#containers
display_button = gp.Container(app)
pwd_len_lbl = gp.Label(display_button, "Length: 0 characters")
submit_btn = gp.Button(display_button, "Check", update_pwd_length)

status_container = gp.Container(app)
status_lbl = gp.StyleLabel(status_container, "No Password")
status_lbl.font_name = 'Noto Sans Myanmar' 
status_lbl.font_size = 28
breach_lbl = gp.StyleLabel(status_container, "Breach Status: Unknown")
breach_lbl.font_name = 'Noto Sans Myanmar' 
breach_lbl.font_size = 23
breach_message = gp.Label(status_container, "")

progress_bar = gp.Progressbar(app, mode="determinate")


fail_lbl = gp.StyleLabel(app, "Required components")
fail_lbl.font_size = 20
weakness_lbl = gp.StyleLabel(app, "Major Weakness")
weakness_lbl.font_size = 20
suggestions_lbl = gp.StyleLabel(app, "Suggestions")
suggestions_lbl.font_size = 20

display_critical = gp.Label(app, "")
display_weakness = gp.Label(app, "")
display_suggestion = gp.Label(app, "")


# Containers
display_button.set_grid(2, 1)
display_button.add(pwd_len_lbl, 1, 1, align="center")
display_button.add(submit_btn, 2, 1, align="center")

status_container.set_grid(3, 1)
status_container.add(status_lbl, 1, 1, align="center")
status_container.add(breach_lbl, 2, 1, align="center")
status_container.add(breach_message, 3, 1, align="center")




# row 1
app.add(logo, 1, 1, align="right")
app.add(heading_label, 1, 2, align="center")
# row 2
app.add(password_lbl, 2, 1, align="right")
app.add(password_input, 2, 2)
app.add(show_pwd, 2, 3, align="left")

# row 3
app.add(display_button, 3, 2, align="center")

# row 4

app.add(status_container, 4, 2, align="center")

# row 5
app.add(progress_bar, 5, 1, column_span=3, fill=True)
 
# row 6
app.add(fail_lbl, 6, 1, align="center")
app.add(weakness_lbl, 6, 2, align="center")
app.add(suggestions_lbl, 6, 3, align="center")

# row 7
app.add(display_critical, 7, 1, align="center")
app.add(display_weakness, 7, 2, align="center")
app.add(display_suggestion, 7, 3, align="center")


app.run()

