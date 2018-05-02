from flask import Flask, request, render_template, redirect, url_for, Response, json

from flask_login import current_user, LoginManager, UserMixin, login_user, logout_user, login_required
from sqlalchemy import exc, update
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
	if not current_user.is_authenticated:
		return render_template ('homePage.html')
	else:
		return redirect(url_for('profilePage'))

@app.route('/addSong')
def addSong():
	return render_template('addSong.html')

@app.route('/addPost')
@login_required
def addPost():
	return render_template('addPost.html')

@app.route('/newPost', methods=['POST'])
@login_required
def newPostHandling():
	userID = current_user.id
	post = request.form['post']
	picture = request.form['optionalPicture']
	if not picture:
		picture = 'https://d30y9cdsu7xlg0.cloudfront.net/png/26260-200.png'
	addPostToDatabase(post, picture)
	return redirect(url_for('profilePage'))

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
	try:
		logout_user()
		return render_template('homePage.html')
	except BuildError:
		return "you must be logged in to access this page"

@app.route('/profile')
@login_required
def profilePage():
	userData = returnUserData(current_user.username)
	print "user dataaaaaaaaaaa"
	print userData
	annotationDataForThisUser = returnAnnotationDataForThisUser(current_user.id)
	print "annotationDataForThisUser = "
	print annotationDataForThisUser
	if str(userData.isArtist) == "1":
		songList = returnArtistSongData(userData.id)
		postList = getPostsForThisArtist(current_user.id)
		return render_template ('artistProfile.html', userData=userData, songList=songList, annotationDataForThisUser=annotationDataForThisUser, postsForThisArtist=postList)
	else:
		# print "is not artist"
		return render_template ('userProfile.html', userData=userData, annotationDataForThisUser=annotationDataForThisUser)



@app.route('/editProfile.html')
@login_required
def editProfileHTML():
	return render_template('editProfile.html')	

@app.route('/editProfile', methods=['GET', 'POST'])
@login_required
def editProfile():
	if request.method == 'POST':
		oldPassword = request.form['oldPassword']
		entered_data = [current_user.username, oldPassword]
		if isUserVerified(entered_data):
			newPassword = str(request.form['pw2'])
			userpassword = sha256_crypt.encrypt(newPassword)
			bio = request.form['bio']
			profilePicture = request.form['profilePicture']
			updatePassword(current_user.id, userpassword, bio, profilePicture)
			return redirect(url_for("profilePage"))
		else:
			print "wrong password"
			return "didnt match"
	else:
		return "Gett"

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
			if str(userData.isArtist) == "1":
				# print "is artist"
				songList = returnArtistSongData(userData.id)
				return redirect(url_for("profilePage"))
				# return render_template ('artistProfile.html', userData=userData, songList=songList)
			else:
				# print "is not artist"
				return redirect(url_for("profilePage"))
				# return render_template ('userProfile.html', userData=userData)
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
		# m=tempAnnotation
		m = tempAnnotation.split('\r\n')
		l = tempAnnotation.splitlines()
		# print l
		# print m[0]
		# print "first elements"
		# print m
		# print "this is temp annote"
		# print tempAnnotation
		# print "ACTUAL SONG"
		print "-----------------------"
		print type(songNumber)
		s = '\n \n'.join(makeSongLyricsList(int(songNumber)))
		splitwise = fillAnnotateTable(int(songNumber)).splitlines()
		# print "im pennywise the dancing clown"
		# print splitwise
		# print "------------- HEREREREE--------------"
		# print tempAnnotation in makeSongLyricsList(1)
		# print allindices (m[0], makeSongLyricsList)
		# print 'hello - '.join(str(e) for e in makeSongLyricsList(1))
		# print ''.join(m)
		# s=s.strip()
		# print "markerrrrrrrrrrrrrr"

		# print s 
		# print "yello 1111111111111111"
		# print '\r\n'.join(m)
		# startingCharacter = s.find('\r\n'.join(m))
		# print "start char"
		# print startingCharacter
		# endingCharacter = startingCharacter + len(''.join(m))
		# print "end char"
		# print endingCharacter

		# print "yello 2222222222"
		startingCharacter1 = s.find(tempAnnotation)
		print "start char"
		print startingCharacter1
		endingCharacter1 = startingCharacter1 + len(''.join(m))
		print "end char"
		print endingCharacter1

		# print "yello 33333333333"
		part = ''.join(l)
		full = ''.join(splitwise)
		startingCharacter2 = full.find(part)
		print "start char"
		print startingCharacter2
		endingCharacter2 = startingCharacter2 + len(''.join(part))
		print "end char"
		print endingCharacter2

		if startingCharacter1 is -1:
			startingCharacter = startingCharacter2 + 15
			endingCharacter = endingCharacter2 +15
		else:
			startingCharacter = startingCharacter1
			endingCharacter = endingCharacter1

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
				startingCharacter = startingCharacter + startline

				# print "startline=" + str(startline)
				catch = True

			if endingCharacter < varArray[i]:
				endline = i + 1
				endingCharacter = endingCharacter + endline

				# end
				# print "endline=" + str(endline)
				break

		catch = False

		for i in range(len(varArray)):
			if startingCharacter < varArray[i] and catch is False:

				startline = i + 1
				catch = True

			if endingCharacter < varArray[i]:
				endline = i + 1
				break

		print tempAnnotation
		print "startline= " + str(startline)
		print "endline= " + str(endline)

		artistid = returnArtistIdFromSongId(songNumber)


		annotateText = Annotations(theAnnotation, current_user.id, songNumber, startline, endline)
		addAnnotationToDatabase (annotateText)
		# return redirect(url_for(song(int(songNumber))))
		# return render_template
		return song(int(songNumber))
		# return "added annotation successfully"

@app.route('/searchQuery', methods=['GET'])
def searchQuery():
	searchQuery = request.args.get('searchQuery')
	data = searchForThisText(searchQuery)
	return render_template('search.html', data=data)

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
			return render_template('allSongs.html', songs=songList, is_authenticated=current_user.is_authenticated)
		else:
			song = returnSong (songNumber)
			annotationDataForThisSong = getAnnotationData(songNumber)
			print annotationDataForThisSong
			temp = allAnnotationLineNumbers(songNumber)
			# print "/////////////////////////"
			print temp
			return render_template('ajaxSongPage.html', is_authenticated=current_user.is_authenticated, songNumber=songNumber, song=song, songs=songList, comments=commentList, allAnnotationLineNumbers=temp, annotationDataForThisSong=annotationDataForThisSong)
			#render ajaxSongPage.html
	except exc.OperationalError:
		return render_template('songDatabaseEmpty.html')

@app.route('/publicArtistProfile')
@app.route('/publicArtistProfile/<int:artistID>')
def publicArtistProfile(artistID = None):
	try:
		if artistID is None:
			allArtistIDs = returnAllArtistIDs()
			return render_template('allArtists.html', is_authenticated=current_user.is_authenticated, allArtistIDs=allArtistIDs)
		else:
			postsForThisArtist = getPostsForThisArtist(artistID)
			thisArtistData = returnUserDataByUserID(artistID)
			return render_template('publicArtistProfiles.html', thisArtistData=thisArtistData, is_authenticated=current_user.is_authenticated, postsForThisArtist=postsForThisArtist)
	except exc.OperationalError:
		return "Posts Database Empty"

@app.errorhandler(404)
def page_not_found(e):
	return "<h1> Error 404: Page not found </h1>"

@app.errorhandler(401)
def page_unauthorized(e):
    return "<h1> Error 401: You must login to view this page. </h1>"

if __name__ == "__main__":
	app.run (host = '0.0.0.0', port=5000)
