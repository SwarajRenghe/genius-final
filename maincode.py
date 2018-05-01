from flask import Flask, request, render_template, redirect, url_for, Response, json
from songs import returnSongs
from flask_login import current_user, LoginManager, UserMixin, login_user, logout_user, login_required
from sqlalchemy import exc
from passlib.hash import sha256_crypt
import json
from sqLite import *

app = Flask (__name__)
app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///executedisshit.db'
app.config['SECRET_KEY'] = 'blessusbabyllama'

login_manager = LoginManager()	
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
	session = Session()
	return session.query(User).get(int(id))
	

@app.route('/')
def homePage():
	return render_template ('homePage.html')

@app.route('/addSong')
def addSong():
	return render_template('addSong.html')

@app.route('/users')
def users ():
	try:
		userList = returnUserDatabase ();
		return render_template('allUsers.html', users=userList)
	except exc.OperationalError:
		return render_template('songDatabaseEmpty.html')


@app.route('/addUser')
def addUser():
	return render_template('addUser.html')

# @app.route('/login')
# def login():
# 	return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return render_template('homePage.html')

@app.route('/loginVerification', methods=['GET', 'POST'])
def loginVerification():
	if request.method == 'POST':

		entered_username = request.form['username']
		entered_password = request.form['password']
		entered_data = [entered_username, entered_password];
		boolean = isUserVerified(entered_data)
		print "CANNOT FIND USER"
		if boolean is True:
			login_user(returnQuery(entered_username))
			print current_user.is_authenticated
			# print "yeeeeeeeeeeeeeeet"
			userData = returnUserData(entered_username)
			# print (userData.isArtist == str(userData.isArtist))
			if str(userData.isArtist) == "checkArtist":
				# print "is artist"
				songList = returnArtistSongData(userData.id)
				return render_template ('artistProfile.html', userData=userData, songList=songList)
			else:
				# print "is not artist"
				return render_template ('userProfile.html', userData=userData)
		else:
			return "false"

	else:
		entered_username = request.args.get('username')
		entered_password = request.args.get('password')
		print "Entered username is " + entered_username
		print "Entered password is " + entered_password
		entered_data = [entered_username, entered_password];
		boolean = isUserVerified (entered_data)
		if boolean is True:
			login_user(returnQuery(entered_username))
			print current_user.is_authenticated
			# print "yeeeeeeeeeeeeeeet"
			userData = returnUserData(entered_username)
			# print (userData.isArtist == str(userData.isArtist))
			if str(userData.isArtist) == "checkArtist":
				# print "is artist"
				songList = returnArtistSongData(userData.id)
				return render_template ('artistProfile.html', userData=userData, songList=songList)
			else:
				# print "is not artist"
				return render_template ('userProfile.html', userData=userData)
		else:
			return "false"

@app.route('/newSongHandlingPage')
@login_required
def newSongHandling():
	if request.method == 'POST':
		# user = request.form['songname']
		s = songClass();
		s.songname = request.form['songname']
		s.albumname = request.form['albumname']
		s.artist = current_user.username
		s.lyric = str(request.form['lyric'])

		s.imglink = request.form['imglink']
		addSongToDatabase(s);
		return render_template("addedSongSuccessfully.html")
		# return user
	else:
		# s = songClass();
		songname = request.args.get('songname')
		albumname = request.args.get('albumname')
		artist = current_user.username
		lyric = request.args.get('lyric')
		imglink = request.args.get('imglink')
		artistID = returnArtistId(artist)
		s = Song(songname, artist, artistID,albumname,lyric,imglink);
		addSongToDatabase(s);
		return render_template("addedSongSuccessfully.html")

def find_substring(substring, string):
    """
    Returns list of indices where substring begins in string

    >>> find_substring('me', "The cat says meow, meow")
    [13, 19]
    """
    indices = []
    index = -1  # Begin at -1 so index + 1 is 0
    while True:
        # Find next index of substring, by starting search from index + 1
        index = string.find(substring, index + 1)
        if index == -1:
            break  # All occurrences have been found
        indices.append(index-1)
    return indices


@app.route('/newCommentPage',methods=['PUT'])
@login_required
def newCommentHandling():
	data=request.get_json()
	print data
	addedComment = data['somment']
	songNumber = data['sumber']
	print addedComment
	print songNumber
	print "this is the end"

	commentingUser = current_user.id
	c = Comments(addedComment, commentingUser, songNumber)
	addCommentToDatabase(c)
		# alert("Your comment has been added")
		# return redirect(url_for("song(songNumber = None)"))
	return Response(
		json.dumps({'message':'successfully updated','upic':current_user.profilePicture,
		'uname':current_user.username}),	
		status=200,
		mimetype='application/json'
		)


@app.route('/newAnnotationPage')
@login_required
def newAnnotationHandling():
	if request.method == 'POST':
		tempAnnotation = request.form['selectedtext']
		songNumber = request.form['buttonForSongNumber']
		print "song number is " + str(songNumber) + "songnum"

		lyrik = fillAnnotateTable(songNumber)
		print lyrik
		varArray = find_substring("\n",lyrik)
		# def getLineNum()
		#     pos =0;
		#     num = -1;
		#     i = -1;
		#     while pos!=-1:
		#         pos = lyrik.indexOf("<br>", i+1)
		#         array.push(pos -  1);
		#         num+=1;
	    #      	i=pos;
	
		print varArray

		print tempAnnotation.split('\n')
		return tempAnnotation
	else:
		tempAnnotation = request.args.get('selectedtext')
		songNumber = request.args.get('buttonForSongNumber')
		theAnnotation = request.args.get('annotationItself')
		# endlineprint "RECIEVED DATA"
		# print songNumber
		tempAnnotation = tempAnnotation[:-1]
		m = tempAnnotation.split('\n')
		# print tempAnnotation
		# print "ACTUAL SONG"
		print "-----------------------"
		print type(songNumber)
		s = ''.join(makeSongLyricsList(int(songNumber)))
		# print "------------- HEREREREE--------------"
		# print tempAnnotation in makeSongLyricsList(1)
		# print allindices (m[0], makeSongLyricsList)
		# print 'hello - '.join(str(e) for e in makeSongLyricsList(1))
		# print ''.join(m)
		startingCharacter = s.find(''.join(m))
		print "start char"
		print startingCharacter
		endingCharacter = startingCharacter + len(''.join(m))
		print "end char"
		print endingCharacter
		# print s.find(m[0])
		# print s.find(m[-1])
		# print songNumber + "songnum"
		lyrik = fillAnnotateTable(songNumber)
		print "----------- lyric is "
		print lyrik
		# print lyrik
		# varArray=[]
		varArray = find_substring("\n", lyrik)
		print varArray
		print "number of elements"

		catch = False
		for i in range(len(varArray)):
			if startingCharacter < varArray[i] and catch is False:
				startline = i + 1
				# print "startline=" + str(startline)
				catch = True

			if endingCharacter < varArray[i]:
				endline = i + 1
				# print "endline=" + str(endline)
				break

		# print tempAnnotation
		print "startline= " + str(startline)
		print "endline= " + str(endline)

		artistid = returnArtistIdFromSongId(songNumber)


		annotateText = Annotations(theAnnotation, current_user.id, songNumber, startline, endline)
		addAnnotationToDatabase (annotateText)
		return "added annotation successfully"


@app.route('/newUserHandlingPage', methods=['GET', 'POST'])
def newUserHandling():
	if request.method == 'POST':
	
		username = request.form['username']
		password = str(request.form['pwd2'])
		userpassword = sha256_crypt.encrypt(password)
		useremail = request.form['email']
		isArtist = request.form.getlist('checkArtist')
		# print isArtist
		bio = request.form['bio']
		profilePicture = request.form['profilePicture']
		if not profilePicture:
			profilePicture = "https://kaggle2.blob.core.windows.net/avatars/images/1629463-kg.jpg"
		if isArtist:
			u = User (username, userpassword, useremail, 1, bio, profilePicture)
		else:
			u = User (username, userpassword, useremail, 0, bio, profilePicture)
		print ("------------------------henlo")
		addUserToDatabase(u);
		return render_template("addedUserSuccessfully.html")
		# return user
	else:
		# x = request.args.get('checkArtist')
		# print x
		username = request.args.get('username')
		password = str(request.args.get('pwd2'))
		userpassword = sha256_crypt.encrypt(password)
		# u.userpassword = request.args.get('userpassword')
		useremail = request.args.get('email')
		isArtist = request.args.get('checkArtist')
		bio =  request.args.get('bio')
		profilePicture =  request.args.get('profilePicture')
		u = User (username, userpassword, useremail, isArtist, bio, profilePicture)
		addUserToDatabase(u);
		return render_template("addedUserSuccessfully.html")


@app.route('/songs')
@app.route('/songs/<int:songNumber>')
def song(songNumber = None):
	try:
		songList = returnSongDatabase ()
		commentList = returnCommentDatabase()

		if songNumber is None:
			return render_template('allSongs.html', songs=songList)
		else:
			song = returnSong (songNumber)
			annotationDataForThisSong = getAnnotationData(songNumber)
			print annotationDataForThisSong
			temp = allAnnotationLineNumbers(songNumber)
			# print "/////////////////////////"
			print temp
			return render_template('individualSongs.html', songNumber=songNumber, song=song, songs=songList, comments=commentList, allAnnotationLineNumbers=temp, annotationDataForThisSong=annotationDataForThisSong)
			#render ajaxSongPage.html
	except exc.OperationalError:
		return render_template('songDatabaseEmpty.html')

# @app.route('')

@app.errorhandler(404)
def page_not_found(e):
	return "<h1> Error 404: Page not found </h1>"

@app.errorhandler(401)
def page_unauthorized(e):
    return "<h1> Error 401: You must login to view this page. </h1>"

if __name__ == "__main__":
	app.run (host = '0.0.0.0', port=5000)
