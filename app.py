import gooeypie as gp



app = gp.GooeyPieApp("Password Checker")
app.width = 800
app.height = 600
app.set_grid(7, 3)


def toggle_pwd_visibility(event):
    password_input.toggle()

def progress_bar_update(score):
    max_score = 5
    progress_bar.value = (score / max_score) * 100

def check_password_length(event): # check password strength
    pwd = password_input.text
    score = 0
    progress_bar.value = 0
    critical_feedback = []
    weakness_feedback = []
    feedback = []
    major_weakness = False
    critical_fail = False

    # length check
    if len(pwd)>= 12:
        score += 3
    elif len(pwd)>= 10:
        score += 2
        feedback.append("- Consider using 12+ characters")
    elif len(pwd) >= 8:
        score += 1
        feedback.append("- Consider using 12+ characters")
    elif len(pwd) >= 6:
        weakness_feedback.append("- Include 8 characters")
        critical_fail = True
    else:
        critical_feedback.append("- INCLUDE 8 CHARACTERS")
        major_weakness = True
    

   # letter check
    if any(char.isdigit() for char in pwd):
        score += 1
    else:
        weakness_feedback.append("- Include one number")
        major_weakness = True

    # Upper case check
    if any(char.isupper() for char in pwd):
        score += 1
    else:
        weakness_feedback.append("- Include one uppercase letter")
        major_weakness = True

    # Lower case check
    if any(char.islower() for char in pwd):
        score += 1
    else:
        feedback.append("- Include one lowercase letter")

    # Special character check
    if any(char in "!@#$%^&*()_+-=[]{}|;:',.<>/?`~" for char in pwd):
        score += 1
    else:
        feedback.append("- Include one special character")

    # Check for common passwords
    critical_fail, critical_feedback = check_common_pwds(pwd, critical_fail, critical_feedback) 

    if critical_fail == True:
        score = 0
    if major_weakness == True:
        score = max(0, score - 1)
        

    # run progress bar 
    progress_bar_update(score)

    # display feedback 
    if critical_feedback == []:
        display_critical.text = "No critical feedback"
    else: 
        display_critical.text = "\n".join(critical_feedback)

    if weakness_feedback == []:
        display_weakness.text = "No major weakness"
    else: 
        display_weakness.text = "\n".join(weakness_feedback)

    if feedback == []:
        display_suggestion.text = "No suggestions"
    else: 
        display_suggestion.text = "\n".join(feedback)

    # result_lbl.text = f"Password score: {score}/5\n"
    # if score == 5:
    #     result_lbl.text += "\nStrong password!"
    # else:
    #     result_lbl.text += "\n" + "\n".join(feedback)

def check_common_pwds(pwd, critical_fail, critical_feedback):
    f = open("/Users/cruzleung/Desktop/school/SEN/11SEN/assessment_2/pwd_checker/txt_files/common_pwdlist.txt")

    common_passwords = f.readlines()
    cleaned_common_pwd = []

    for password in common_passwords: 
        password = password.replace("\n", "")
        cleaned_common_pwd.append(password)

    if pwd in cleaned_common_pwd:
        critical_fail = True
        critical_feedback.append("- FOUND IN TOP 1000 PASSWORDS" + "\n  Choose something more unique")
    return critical_fail, critical_feedback
        




# labels 

styled_label = gp.StyleLabel(app, "PASSWORD STRENGTHENER")
styled_label.font_name = "Aerial"
styled_label.color = "red"
styled_label.font_size = 20
styled_label.align = 'right'


password_lbl = gp.Label(app, "Password")

password_input = gp.Secret(app)
password_input.justify = 'left'
password_input.width = 50
show_pwd = gp.Checkbox(app, "Show Password")
show_pwd.add_event_listener("change", toggle_pwd_visibility)

display_button = gp.Container(app)
pwd_len_lbl = gp.Label(display_button, "<pwdlength>")
submit_btn = gp.Button(display_button, "Check", check_password_length)

# Container for the progress bar and status messages
status_bar = gp.Container(app)
status_lbl = gp.StyleLabel(app, "<status>")
status_lbl.font_name = "Aerial"
status_lbl.font_size = 20
progress_bar = gp.Progressbar(app, mode="determinate")

# suggestions_lbl = gp.Label(app, "Suggestions:")
fail_lbl = gp.StyleLabel(app, "CRITICAL WEAKNESS")
fail_lbl.font_size = 20
weakness_lbl = gp.StyleLabel(app, "MAJOR WEAKNESS")
weakness_lbl.font_size = 20
sugesstions_lbl = gp.StyleLabel(app, "SUGGESTIONS")
sugesstions_lbl.font_size = 20

# result_lbl= gp.Label(app, "")
display_critical = gp.Label(app, "")
display_weakness = gp.Label(app, "")
display_suggestion = gp.Label(app, "")


# Add widgets to container
display_button.set_grid(1, 2)
display_button.add(pwd_len_lbl, 1, 1, align="center")
display_button.add(submit_btn, 1, 2, align="center")

# row 1
app.add(styled_label, 1, 2, align="center")
# row 2
app.add(password_lbl, 2, 1, align="right")
app.add(password_input, 2, 2)
app.add(show_pwd, 2, 3, align="left")
# row 3

app.add(display_button, 3, 2, align="center")
# row 4
# app.add(status_bar, 4, 2, align="center")
app.add(status_lbl, 4, 2, align="center")
# row 5
app.add(progress_bar, 5, 1, column_span=3, fill=True)
 
# row 6
# app.add(suggestions_lbl, 6, 1, align="center")
# app.add(result_lbl, 6, 2, align="center")
app.add(fail_lbl, 6, 1, align="center")
app.add(weakness_lbl, 6, 2, align="center")
app.add(sugesstions_lbl, 6, 3, align="center")

#row 7
app.add(display_critical, 7, 1, align="center")
app.add(display_weakness, 7, 2, align="center")
app.add(display_suggestion, 7, 3, align="center")


app.run()

