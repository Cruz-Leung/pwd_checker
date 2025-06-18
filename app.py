import gooeypie as gp
import re
from sequential_database import sequential_patterns
import hashlib
import requests
import string
from random import choice

password_cache = {}  # Cache for password breach checks

app = gp.GooeyPieApp("Password Checker")
app.width = 1200
app.height = 700
app.set_grid(7, 3)


def check_exit():
    ok_to_exit = app.confirm_yesno('Really?', 'Are you sure you want to close?', 'question')
    return ok_to_exit

def toggle_pwd_visibility(event):
    password_input.toggle()

def progress_bar_update(score):
    max_score = 7
    percent = int((score / max_score) * 100)
    progress_bar.value = max(0, min(percent, 100))
    
### Update password length label and check password strength
def update_pwd_length(event):
    pwd = password_input.text

    pwd_len_lbl.text = f"Length: {len(pwd)} characters"
          

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
        # progress_bar.value = 0
        return 0
    
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
    # breached_fail, breach_message = breached_password_check(pwd, breached_fail)
    major_weakness_count, weakness_feedback = repeated_pattern_check(pwd, major_weakness_count, weakness_feedback)
    response = check_password_pwned(pwd, password_cache)
   


    ### Calculate final score
    # if requirement_fail == True:
    #     score = 0
    # try:
    #     response = check_password_pwned(pwd, password_cache)
    # except Exception as e:
    #     print(f"API error: {e}")
    #     response = -1

    score -= min(major_weakness_count, 4) # limit weakness penalty to maximum 3 points
    score = max(score, 0)  # Ensure score is not negative

    
    if response == -1:
        breach_lbl.text = "Breach Status: Error"
        breach_lbl.color = "#ffa500"
        breach_message.text = "Error checking password breach status."
    elif response > 0:
        score = 0
        breach_lbl.text = "Breach Status: Breached"
        breach_lbl.color = "#ff0000"
        breach_message.text = f"This password was found in {response} known data breaches."
    else: 
        breach_lbl.text = "Breach Status: Not Breached"
        breach_lbl.color = "#48ff00"
        breach_message.text = "Password not found in known data breaches."

    # Update status label
    strength_status(score)
        
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
        display_suggestion.text = "No addtional suggestions"
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

def check_password_pwned(pwd, password_cache):
    if pwd in password_cache:
        return password_cache[pwd]
    
    sha1_password = hashlib.sha1(pwd.encode('utf-8')).hexdigest().upper()
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"API error: {e}")
        app.alert("Error", "Please try again")
        return -1  # Indicate error

    hashes = (line.split(':') for line in res.text.splitlines())
    for h, count in hashes:
        if h == suffix:
            password_cache[pwd] = int(count)
            return int(count)  # Number of times password was found
        
    password_cache[pwd] = 0
    return 0  # Password not found
    

### REPEATED CHARACTER AND PATTERN CHECK
### Looked up python module re for regular expressions with some AI assistant and self editing to suit code
def repeated_pattern_check(pwd, major_weakness_count, weakness_feedback):
    lower_pwd = pwd.lower()
    breached_fail = True
#             breach_count = int(entry['count'])
#             return breached_fail, breach_count  # Return immediately if found
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
    


def strength_status(score):
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
        
def open_about_window(event):
    about_window.show()

def password_generator(event):
    generator_window.show()

def show_generated_password(event):
    generator_input_pwd.text = generate_password()


def generate_password(): 
    length = 12
    available_chars = ''
    available_chars += string.ascii_letters
    available_chars += string.digits * 2 + string.punctuation # double the digits to increase chance of having a number as there are only 10 digits 
    
    # Make the password
    new_password = ''
    for count in range(length):
        new_password += choice(available_chars)
    return new_password

def copy_password(event):
    app.copy_to_clipboard(generator_input_pwd.text)
######### LABELS AND INPUTS ##########

# logo 
logo = gp.Image(app, "/Users/cruzleung/Desktop/school/SEN/11SEN/assessment_2/pwd_checker/images/logo.png")

### Test Label
heading_label = gp.StyleLabel(app, 'Password Strengthener')
heading_label.font_name = 'Noto Sans Myanmar'
heading_label.font_size = 32
heading_label.font_weight = 'bold'

# Window for about button
about_button = gp.Button(app, "About", open_about_window)
about_window = gp.Window(app, "About")
# Window 
about_window.height = 50
about_window.width = 300
about_window.set_grid(3, 1)
about_lbl = gp.Label(about_window, "        Version 1.0.0\nCreated by Cruz Leung")
about_window.add(about_lbl, 1, 1, align="center")
usage_lbl= gp.StyleLabel(about_window, "How to use")
usage_lbl.font_name = 'Noto Sans Myanmar'
usage_lbl.font_size = 20
usage_lbl.font_weight = 'bold'
about_window.add(usage_lbl, 2, 1, align="center")
usage_text = gp.Label(about_window, " 1. Enter a password in the input box \n 2. Click 'Check'\n 3. Follow the feedback to improve your password \n\n Note: This app does not store or save your passwords")
about_window.add(usage_text, 3, 1, align="center")

password_lbl = gp.Label(app, "Password")

password_input = gp.Secret(app)
password_input.add_event_listener('change', update_pwd_length)
password_input.justify = 'left'
password_input.width = 50
show_pwd = gp.Checkbox(app, "Show Password")
show_pwd.add_event_listener("change", toggle_pwd_visibility)

#containers
display_button = gp.Container(app)
pwd_len_lbl = gp.Label(display_button, "Length: 0 characters")
submit_btn = gp.Button(display_button, "Check", check_password)

# Password Generator button
pwd_generator_btn = gp.Button(display_button, "Generate Password", password_generator)
generator_window = gp.Window(app, "Password Generator")
generator_window.height = 50
generator_window.width = 300
generator_window.set_grid(4, 1)
# Generator window
generator_lbl = gp.StyleLabel(generator_window, "Generate Password")
generator_lbl.font_name = 'Noto Sans Myanmar'
generator_lbl.font_size = 20
generator_lbl.font_weight = 'bold'
generator_window.add(generator_lbl, 1, 1, align="center")
generator_input_pwd = gp.Input(generator_window)
generator_window.add(generator_input_pwd, 2, 1, fill=True, stretch=True)
generator_window_button = gp.Button(generator_window, "Generate Password", show_generated_password)
generator_window.add(generator_window_button, 4, 1, align="center")
copy_btn = gp.Button(generator_window, 'Copy to Clipboard', copy_password)
generator_window.add(copy_btn, 3, 1, align="center")
copy_btn.width = 15


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
display_button.set_grid(3, 1)
display_button.add(pwd_len_lbl, 1, 1, align="center")
# Password Generator
display_button.add(submit_btn, 2, 1, align="center")
display_button.add(pwd_generator_btn, 3, 1, align="center")


status_container.set_grid(3, 1)
status_container.add(status_lbl, 1, 1, align="center")
status_container.add(breach_lbl, 2, 1, align="center")
status_container.add(breach_message, 3, 1, align="center")



# row 1
app.add(logo, 1, 1, align="right")
app.add(heading_label, 1, 2, align="center")
app.add(about_button, 1, 3, align="left")
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

app.on_close(check_exit)

app.run()

