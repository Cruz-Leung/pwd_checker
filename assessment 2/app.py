import gooeypie as gp

WIDTH = 500
HEIGHT = 700


app = gp.GooeyPieApp("Password Checker")
app.set_grid(5, 3)

def toggle_pwd_visibility(event):
    password_input.toggle()

def progress_bar_update(score):
    max_score = 5
    progress_bar.value = (score / max_score) * 100

def check_password_length(event): # check password strength
    pwd = password_input.text
    score = 0
    progress_bar.value = 0
    feedback = []
    major_weakness = False
    critical_fail = False

    # length check
    if len(pwd) >= 8:
        score += 1
    elif len(pwd) >= 6:
        feedback.append("CRITICAL FAIL - INCLUDE 8 CHARACTERS")
        critical_fail = True
    else:
        feedback.append("MAJOR WEAKNESS - Include 8 characters")
        major_weakness = True
    

   # letter check
    if any(char.isdigit() for char in pwd):
        score += 1
    else:
        feedback.append("MAJOR WEAKNESS - Inclucd one number")
        major_weakness = True

    # Upper case check
    if any(char.isupper() for char in pwd):
        score += 1
    else:
        feedback.append("MAJOR WEAKNESS - Include one uppercase letter")
        major_weakness = True

    # Lower case check
    if any(char.islower() for char in pwd):
        score += 1
    else:
        feedback.append("Include one lowercase letter")

    # Special character check
    if any(char in "!@#$%^&*()_+-=[]{}|;:',.<>/?`~" for char in pwd):
        score += 1
    else:
        feedback.append("Include one special character")

    if critical_fail == True:
        score = 0
    if major_weakness == True:
        score = max(0, score - 1)
        

    critical_fail, feedback = check_common_pwds(pwd, critical_fail, major_weakness) 
    # run progress bar 
    progress_bar_update(score)



    # Set feedback and score
    result_lbl.text = f"Password score: {score}/5\n"
    if score == 5:
        result_lbl.text += "\nStrong password!"
    else:
        result_lbl.text += "\n" + "\n".join(feedback)

def check_common_pwds(pwd, critical_fail, feedback):
    f = open("txt_files/common_pwdlist.txt")

    common_passwords = f.readlines()
    cleaned_common_pwd = []

    for password in common_passwords: 
        password = password.replace("\n", "")
        cleaned_common_pwd.append(password)

    if pwd in cleaned_common_pwd:
        critical_fail = True
        result_lbl.text += ("common")
        feedback.append("CRITICAL FAIL - Password is too common")
    return critical_fail, feedback
        





styled_label = gp.StyleLabel(app, "PASSWORD STRENGTHENER")
styled_label.font_name = "Aerial"
styled_label.color = "red"


styled_label.font_size = 15
styled_label.align = 'right'


password_lbl = gp.Label(app, "Password")
password_input = gp.Secret(app)
password_input.justify = 'left'
password_input.width = 50
show_pwd = gp.Checkbox(app, "Show Password")
show_pwd.add_event_listener("change", toggle_pwd_visibility)
submit_btn = gp.Button(app, "Check", check_password_length)
progress_bar = gp.Progressbar(app, mode="determinate")
suggestions_lbl = gp.Label(app, "Suggestions:")
result_lbl= gp.Label(app, "")



app.add(styled_label, 1, 2, align="center")
app.add(password_lbl, 2, 1, align="right")
app.add(password_input, 2, 2)
app.add(show_pwd, 2, 3, align="left")
app.add(submit_btn, 3, 2, align="center")
app.add(progress_bar, 4, 1, column_span=2, fill=True)
app.add(suggestions_lbl, 5, 1, align="center")
app.add(result_lbl, 5, 2, align="center")




app.run()

