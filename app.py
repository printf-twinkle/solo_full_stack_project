from flask import Flask, render_template, request, url_for, redirect, session
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import updated_save_ques,all_details,get_user1,save_ques,get_exist_s,get_exist_f,get_ques_name_from_id,get_usname_from_roll,get_ques_id,get_all_marks,get_roll_name,get_current_id,current_id,get_marks_original,save_marks,change_password, get_marks,get_pass,max_uid,get_user, account_exist,get_faculty_data,get_student_data,  get_ques_data,add_faculty,add_student, get_uid,get_ip_op
import subprocess,os
from subprocess import PIPE
from util_tools import send_mail
from user import User
app = Flask(__name__)
app.config['SECRET_KEY'] = '**'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'home'
login_manager.init_app(app)


@app.route('/')
def home():
	if current_user.is_authenticated:
		if current_user.get_user_type() == 1:
			return redirect(url_for('student'))
		if current_user.get_user_type() == 2:
			return redirect(url_for('faculty'))
		if current_user.get_user_type() == 3:
			return redirect(url_for('admin'))
	return render_template("home.html")

@app.route('/change_pass',methods=["POST","GET"])
@login_required
def chngepswd():
	msg=""
	if request.method=="POST":
		err_msg=""
		np=request.form["newpass"]
		cnp=request.form["confnewpass"]
		if np != cnp:
			return render_template("change_pass.html",err_msg="New and confirm new passwords do not match!")
		s=current_user.get_id()
		change_password(s,cnp)
		return render_template("change_pass.html",msg="Password has been changed successfully!")
	return render_template("change_pass.html")

@app.route('/forgotpass',methods=["POST","GET"])
def forgotpass():
	msg=""
	err_msg=""
	if request.method=="POST":
		getmail=request.form["sendmail"]
		s=get_pass(getmail)
		print(s)
		if s ==None:
			return render_template("forgotpass.html",err_msg="This email-id does not exist!")
		send_mail(getmail,s)
		return render_template("forgotpass.html",msg="Email sent!")
	return render_template("forgotpass.html")


@app.route('/login', methods=["POST"])
def usr_login():
    error_msg = ""
    if request.method=="POST":
        user_name=request.form["uname"]
        pswd=request.form["pswd"]
        usr=get_user(user_name,pswd)
        if usr:
            login_user(usr,remember=True)
            if current_user.get_user_type() == 1:
                return redirect(url_for('student'))
            if current_user.get_user_type()==2:
                return redirect(url_for('faculty'))
            if current_user.get_user_type()==3:
                return redirect(url_for('admin'))
        return render_template("home.html",error_msg="Login failed!")
    return redirect(url_for("home"))

@app.route("/student",methods=["POST","GET"])
@login_required
def student():
    s=current_user.get_name()
    return render_template("student_home.html",s=s)

@app.route("/stu_info",methods=["POST","GET"])
@login_required
def stu_info():
	x=get_student_data(current_user.get_id())
	print(x)
	name=x.get("Name")
	em=x.get("Email")
	rn=x.get("Roll Number")
	yos=x.get("Year of Study")
	return render_template("stu_info.html",name=name,em=em,rn=rn,yos=yos)
	#print(name,em,rn,yos)

@app.route("/stu_report",methods=["POST","GET"])
@login_required
def stu_report():
	arg_to_be_rendered = []
	a=get_ques_id()
	x=get_roll_name()
	for p in a:
		ques_id_dict = {}
		ques_id_dict['question_id'] = p
		ques_id_dict['question_name'] = get_ques_name_from_id(p)
		ques_id_dict['student_marks'] = []
		for i in x:
			roll_number = i["Roll Number"]
			stu_name=i["Name"]
			student_marks_dict = {}
			student_marks_dict['roll_number'] = roll_number
			student_marks_dict['stu_name'] = stu_name
			user_name = get_usname_from_roll(roll_number)
			student_marks_dict['user_name'] = user_name
			student_marks_dict['marks_obtained'] = get_all_marks(user_name,p)
			if student_marks_dict['marks_obtained'] ==None:
				student_marks_dict['marks_obtained'] = 'Absent'
			ques_id_dict['student_marks'].append(student_marks_dict)
			
			
		print("ques_id_dict :-" , ques_id_dict)
		arg_to_be_rendered.append(ques_id_dict)
		#ques_id_dict = sorted(ques_id_dict, key=lambda i: i['roll_number'])
		ques_id_dict['student_marks'] = sorted(ques_id_dict['student_marks'], key=lambda i: i['roll_number'])
		print("args_to_be_rendered :-", arg_to_be_rendered)
	return render_template("student_report.html",arg_to_be_rendered = arg_to_be_rendered)

@app.route("/existing_f")
@login_required
def existing_f():
	fe=get_exist_f()
	return render_template("fe.html",fe=fe)

@app.route("/existing_s")
@login_required
def existing_s():
	se=get_exist_s()
	return render_template("se.html",se=se)

@app.route("/faculty",methods=["POST","GET"])
@login_required
def faculty():
    f=current_user.get_name()
    return render_template("faculty_home.html",f=f)

@app.route("/ques_upload",methods=["POST","GET"])
@login_required
def Ques_upload():
	f=0
	if request.method=="POST":
		res=list(request.form.values())
		exam_name=res[0]
		exam_date=res[2]
		exam_det=res[1]
		ques_num=res[3]
		ques_title=res[4]
		uid=max_uid()
		exam_id=exam_name+exam_date
		ques_det=res[5]
		exec_time=res[6]
		marks=res[7]
		inp1=res[8:12:2]
		out1=res[9:12:2]
		save_ques({'Exam_date':exam_date,'Exam name':exam_name,'Exam details':exam_det,'Question number':ques_num,'Question title':ques_title, 'Unique question id':uid, 'Unique exam id':exam_id, 'Question details': ques_det,'Execution time':exec_time,'Marks':marks,'Inputs':inp1,'Outputs':out1})
		f=1
		render_template("questions.html",f=f)
	return render_template("questions.html")

@app.route("/display",methods=["POST","GET"])
@login_required
def display():
    info=get_ques_data()
    print("printing info",info)
    if not info:
        info=''
    return render_template("ques_display.html",info=info)
    
@app.route("/display_details",methods=["POST","GET"])
@login_required
def display_details():
	if request.method=="POST":
		print("Request body ------ ", request.form)
		exam_quest_dict = {}
		exam_quest_dict['Exam_date']=request.form["dt"]
		exam_quest_dict['Exam name']=request.form["en"]
		exam_quest_dict['Exam details']=request.form["ed"]
		exam_quest_dict['Question number']=request.form["qn"]
		exam_quest_dict['Question title']=request.form["qt"]
		exam_quest_dict['Question details']=request.form["qd"]
		exam_quest_dict['Execution time']=request.form["et"]
		exam_quest_dict['Marks']=request.form["ms"]
		exam_quest_dict['Inputs']=request.form["ip"]
		exam_quest_dict['Outputs']=request.form["op"]
		exam_quest_dict["Unique question id"]=int(request.form["quid"])
		print(exam_quest_dict)
		updated_save_ques(exam_quest_dict)
	x = all_details()
	print(x)
	return render_template("display_all.html",x=x)

@app.route('/code_main/<uid>')
@login_required
def Compiler(uid):
	if current_user.get_user_type() == 1:
		me=current_user.get_id()
		x=current_id(me,int(uid))
		y=get_current_id(me)
		s=get_uid(uid)
		title=s[0]
		details=s[1]
		return render_template('code_write.html',title=title,details=details)
	return "<h1>I will design it later!!"

@app.route("/admin",methods=["POST","GET"])
@login_required
def admin():
    a=current_user.get_name()
    return render_template("admin_home.html",a=a)

@app.route("/new_fac",methods=["POST","GET"])
def new_fac():
	if request.method=="POST":
		fn=request.form['fn']
		em=request.form['em']
		pw=request.form['pw']
		if account_exist(em):
			return render_template("fac_reg.html", error_msg="Account already exists with this email!")
		add_faculty(fn,em,pw)
		return redirect(url_for('home'))
	return render_template('fac_reg.html')

@app.route("/new_stu",methods=["POST","GET"])
def new_stu():
	if request.method=="POST":
		fn1=request.form['fn1']
		roll=request.form['roll']
		yr=request.form['yr']
		em1=request.form['em1']
		pw1=request.form['pw1']
		if account_exist(em1):
			return render_template("stu_reg.html", error_msg="Account already exists with this email!")
		add_student(fn1,roll,yr,em1,pw1)
		return redirect(url_for('home'))
	return render_template('stu_reg.html')

@app.route("/results",methods=["GET","POST"])
def results():
	s=current_user.get_id()
	print(s)
	print(type(s))
	y=get_marks(s)
	return render_template("results.html",y=y)

#-----------------------------------------------------------------------------------------------------------------------------
# the c code logic!!
#DO NOT TAMPER.

@app.route('/submit',methods=['GET','POST'])
@login_required
def submit():
	inst="HIDDEN TEST CASE RESULTS AS PER YOUR CODE-"
	c=get_current_id(current_user.get_id())
	s=get_uid(c)
	title=s[0]
	details=s[1]
	if request.method=='POST':
		code=request.form['code']
		inp=request.form['input']
		chk=request.form.get('check')
		if  not chk=='1': 
			inp=""
			check=''
		else:
			check='checked'		
		output=complier_output(code,inp,chk)
	passed,failed=check_standard(code,output,chk)
	return render_template('code_write.html',code=code,input=inp,output=output,check=check,passed=passed,failed=failed,inst=inst,title=title,details=details)
	
 

@app.route('/check_standard',methods=['GET','POST'])
@login_required
def check_standard(code,output,check):
	gio=get_ip_op(get_current_id(current_user.get_id()))
	stand_ip=gio[0]
	notc=len(stand_ip)
	stand_op=gio[1]
	a=[]
	b=[]
	passed=[]
	failed=[]
	c=0
	print(stand_ip)
	for i,j in zip(stand_ip,stand_op):
		a=list(j)
		s=complier_output(code,str(i),check)
		b=list(s)
		f=0
		print("stand:",a)
		print("user:",b)
		if a==b:
			print("Passed!!!!")
			passed.append("Test case passed")
			c+=1
			
		else:
			print("Failed!!!")
			failed.append("Test case failed")
			
	#cal_marks=(get_marks(current_user.get_id())/notc)*c
	print("lalaaaaaa",get_current_id(current_user.get_id()))
	cu=get_current_id(current_user.get_id())
	print("printing ques id",cu)
	cal_marks=(int(get_marks_original(cu))/notc)*c
	print(cal_marks)
	me=current_user.get_id()
	which_ques=get_current_id(current_user.get_id())
	save_marks(me,which_ques,cal_marks)
	return passed,failed
 
			
def complier_output(code,inp,chk):
	if not os.path.exists('Try.c'):
		os.open('Try.c',os.O_CREAT)	
	fd=os.open("Try.c",os.O_WRONLY)
	os.truncate(fd,0)
	fileadd=str.encode(code)
	os.write(fd,fileadd)
	os.close(fd)
	s=subprocess.run(['gcc','-o','new','Try.c'],stderr=PIPE,)
	check=s.returncode
	if check==0:
		if chk=='1':
			r=subprocess.run(["./new"],input=inp.encode(),stdout=PIPE)
		else:
			r=subprocess.run(["./new"],stdout=PIPE)
		return r.stdout.decode("utf-8")
	else:
		return s.stderr.decode("utf-8")


#-----------------------------------------------------------------------------------------------------------------------------------
 
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(username):
	return get_user1(username)

if __name__=='__main__':
    app.run(debug=True)

