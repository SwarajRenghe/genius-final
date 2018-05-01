from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Date
from passlib.hash import sha256_crypt
from flask_login import UserMixin
# from maincode import app

engine = create_engine ("sqlite:///executedisshit.db", echo=True)
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///executedisshit.db'
# app.config['SECRET KEY'] = 'blessusbabyllama'
# SECRET_KEY = 'blessusbabyllama'


Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()



class Comments (Base):
    __tablename__ = 'comments'
    c_id = Column(Integer, primary_key = True, autoincrement = True)
    comm_desc = Column(String, nullable = False)
    id = Column(Integer, ForeignKey('users.id'))
    song_id = Column(Integer, ForeignKey('songs.songnumber'))

    def __init__(self, comm_desc, id, song_id):
        self.comm_desc = comm_desc
        self.id = id
        self.song_id = song_id

def addCommentToDatabase(comm):
    session = Session()
    Base.metadata.create_all(engine)
    temp = Comments (comm.comm_desc, comm.id, comm.song_id)
    session.add(temp)
    session.commit()
    session.close()

def returnCommentDatabase ():
    session = Session()
    commentList = []
    comments = session.query(Comments).all()
    for i in comments:
        commentList.append (i);
    session.close()
    return commentList



class Annotations (Base):
    __tablename__ = 'annotations'
    ann_id = Column(Integer, primary_key = True, autoincrement = True)
    ann_desc = Column(String, nullable = False)
    id = Column(Integer, ForeignKey('users.id'))
    song_id = Column(Integer, ForeignKey('songs.songnumber'))
    range_beg = Column(Integer, nullable = False)
    range_end = Column(Integer, nullable = False)
    upvotes  = Column(Integer)

    def __init__(self, ann_desc, id, song_id, range_beg, range_end):
        self.ann_desc = ann_desc
        self.id = id
        self.song_id = song_id
        self.range_beg = range_beg
        self.range_end = range_end


def numberOfNewLines (s) :
    m = s.count("<br /><br>")
    return m


def addAnnotationToDatabase(annotation):
    session = Session()
    Base.metadata.create_all(engine)
    temp = Annotations (annotation.ann_desc, annotation.id, annotation.song_id, annotation.range_beg, annotation.range_end)
    session.add(temp)
    session.commit()
    session.close()

def allAnnotationLineNumbers(songNumber):
    session = Session()
    annotations = session.query(Annotations).all()
    points = []
    for i in annotations:
        # print "once"
        if i.song_id is songNumber:
            temp = []
            x = i.range_beg
            while x <= i.range_end:
                temp.append(x)
                x+=1
            points.append(temp)
    return list({x for _list in points for x in _list})
    # return points

# print allAnnotationLineNumbers()

def getAnnotationData (songNumber):
    session = Session()
    annotationDataForThisSong = []
    query1 = session.query(Annotations).filter_by(song_id = songNumber).all()
    for i in query1:
        temp = []
        query2 = session.query(User).filter_by(id = i.id).first()
        temp.append(i.ann_desc)
        temp.append(query2.username)
        temp.append(i.range_beg)
        temp.append(i.range_end)
        temp.append(i.upvotes)
        annotationDataForThisSong.append(temp)
    return annotationDataForThisSong


class User (UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique = True, nullable=False)
    password = Column(String, nullable=False)
    isArtist = Column(Integer)
    bio = Column(String)
    # experience = Column(Integer)
    profilePicture = Column(String)
    email = Column(String, unique=True, nullable=False)
    annotate = relationship('Annotations',
        backref=backref('ann_users', lazy='joined')
    )
    comment = relationship('Comments',
        backref=backref('comm_users', lazy='joined')
    )
    singer = relationship('Song',
        backref=backref('art_users', lazy='joined'),
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, username,password,email,isArtist, bio, profilePicture):

        self.username = username
        self.password = password
        self.email = email
        self.bio = bio
        self.isArtist = isArtist
        self.profilePicture = profilePicture

def returnUserData (username):
	session = Session()
	query = session.query(User).filter_by(username = username).first()
	userData = userClass()
	userData.id = query.id
	userData.username = username
	userData.email = query.email
	userData.bio = query.bio
	userData.isArtist = query.isArtist
	userData.profilePicture = query.profilePicture
	session.close()
	return userData

def addUserToDatabase (user):
    session = Session()
    Base.metadata.create_all(engine)

    temp = User(user.username, user.password, user.email, user.isArtist, user.bio, user.profilePicture)

    session.add(temp)
    session.commit()
    session.close()

def returnQuery (username):
	session = Session()
	query = session.query(User).filter_by(username = username).first()
	session.close()
	return query

def isUserVerified(entered_data) :
    session = Session()
    # query = session.query(User).filter_by(username="swaraj")
    # query = session.query(User).filter(User.username.in_(["swaraj"]))
    try:
        query = session.query(User).filter_by(username=entered_data[0]).first()
        # print query.userpassword
        if sha256_crypt.verify(entered_data[1], str(query.password)):
        	print "found in db "
        	return True
        else:
            return False
    # query = session.query(User).filter(User.username.in_([login_username]))
    except AttributeError:
        print "user not in database"


class Song (Base):
    __tablename__ = 'songs'
    songnumber = Column (Integer, primary_key = True, autoincrement=True)
    songname = Column (String, nullable = False)
    albumname = Column (String)
    artist = Column (String, nullable = False)
    artist_id = Column(Integer, ForeignKey('users.id'), nullable= False)
    lyric = Column (String, nullable = False)
    imglink = Column (String)
    song_annotate = relationship('Annotations',
        backref=backref('ann_song', lazy='joined')
    )
    song_comment = relationship('Comments',
        backref=backref('comm_song', lazy='joined')
    )

    def __init__(self, songname,artist,artist_id,albumname,lyric, imglink):
        self.songname = songname
        self.artist = artist
        self.artist_id = artist_id
        self.albumname = albumname
        self.lyric = lyric
        self.imglink = imglink


def addSongToDatabase (song):
    session = Session()
    Base.metadata.create_all(engine)
    temp = Song(song.songname, song.artist, song.artist_id, song.albumname, song.lyric, song.imglink)
    session.add(temp)
    session.commit()
    session.close()

def returnArtistId(artistname):
    session = Session()
    query = session.query(User).filter_by(username = artistname).first()
    if query:
        artistID = query.id
        session.close()
        return artistID

def returnArtistIdFromSongId(songNumber):
    session = Session()
    query = session.query(Song).filter_by(songnumber = songNumber).first()
    session.close()
    return query.artist_id

def returnArtistSongData (artistID):
    session = Session()
    Base.metadata.create_all(engine)
    songList = []
    songs = session.query(Song).all()
    for i in songs:
        if i.artist_id is artistID:
            songList.append(i)
    return songList

def returnSong (songID):
    session = Session()
    song = []
    lines = []
    temp = ''
    query = session.query(Song).filter_by(songnumber = songID).first()
    for i in query.lyric:
        if i != u'\n':
            temp += i
        else:
            lines.append(temp)
            temp=''
    song.append(songID);
    song.append(query.songname)
    song.append(query.artist)
    song.append(query.albumname)
    song.append(query.imglink)
    song.append(lines)
    return song

print returnSong (1)

def fillAnnotateTable(songnum):
    session = Session()
    query = session.query(Song).filter_by(songnumber=songnum).first()
    lyrik = query.lyric
    session.close()
    return lyrik

def makeSongLyricsList(songID):
    session = Session()
    theSongIWant = None
    songs = session.query(Song).all()
    for i in songs:
        if i.songnumber is songID:
            return i.lyric.split('\n')

def printSongDatabase ():
    session = Session()
    songs = session.query(Song).all()
    for i in songs:
        print (str(i.songnumber) + ". " + i.songname + " - " + i.artist)
    session.close()

def returnSongDatabase ():
    session = Session()
    songList = []
    songs = session.query(Song).all()
    for i in songs:
        songList.append (i)
    session.close()
    return songList

def printSongList ():
    # session = Session()
    songs = session.query(Song).all()
    for i in songs:
        print (str(i.songnumber) + ". " + i.songname + " - " + i.artist)


class userClass:
	id = None
	username = None
	useremail = None
	userbio = None
	isArtist = None
	profilePicture = None

class songClass:
	songnumber = None
	songname = None
	artist = None
	imglink = None
