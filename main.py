import re
import hashlib
from user import UserCreate, UserInfo, Friends
import models
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError


def check_password(password):
    # Check if password meets the requirements
    if len(password) < 8 or len(password) > 12:
        print("Password must be between 8 and 12 characters.")
        return False
    if not re.search(r'[A-Z]', password):
        print("Password must contain at least one capital letter.")
        return False
    if not re.search(r'\d', password):
        print("Password must contain at least one digit.")
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        print("Password must contain at least one special character.")
        return False
    return True


def find_user_by_first_last_name(first_name: str, last_name: str, db: Session):
    if db.query(models.User).filter(and_(models.User.first_name == first_name, models.User.last_name == last_name)).first():
        print("Person is a part of the InCollege system")
        signup(db)
    else:
        print("They are not a part of the InCollege system") 
        print("Goodbye")







def find_user_by_first_last_name_login(first_name: str, last_name: str, userData:UserInfo, db: Session):
    if db.query(models.User).filter(and_(models.User.first_name == first_name, models.User.last_name == last_name)).first():
        print("Person is a part of the InCollege system")
        signup(db)
    else:
        print("They are not a part of the InCollege system")
        new_prospective_connection = models.ProspectiveConnection(caller_id=userData.id, first_name=first_name, last_name=last_name)
        db.add(new_prospective_connection)
        db.commit()
        main_hub(userData, db)
        print("Goodbye")








def signup(db):
    # Get user input
    print("Sarah, a determined college student majoring in marketing, faced challenges in finding internships and entry-level positions that aligned with her goals. However, her journey took a positive turn when she discovered InCollege, a specialized job search website for college students. This platform provided curated job listings, networking opportunities, and time-saving tools tailored to Sarah's needs. With InCollege's support, Sarah secured a dream internship at a tech startup, built a strong professional network, and experienced both academic and professional growth. Ultimately, Sarah's success story highlights how leveraging specialized resources can empower college students to kickstart their careers and achieve their goals", "\n")

    print("Welcome to InCollege: Where you can find your dream job, make new friends, and learn new skills.", "\n")
    ans = input("Would you like to view success video? (yes/no): ")
    if ans.lower() == 'yes':
        print("Video playing at https://www.youtube.com/watch?v=dQw4w9WgXcQ", "\n")

    has_account = input("Do you already have an account? (yes/no): ")
    if has_account.lower() == 'yes':
        login(db)
        return
    choice = str(input("Would you like to sign up? (yes/no): "))
    if choice.lower() == 'no':
        choiceFind = str(
            input("Would you like to find a user by first and last name? (yes/no): "))
        if choiceFind.lower() == 'yes':
            first_name = input("Enter the first name of the user: ")
            last_name = input("Enter the last name of the user: ", "\n")
            find_user_by_first_last_name(first_name, last_name, db)
            return
        else:
            print("Goodbye")
            return

    hashed_password = input("Enter your password: ")

    # Check password
    if check_password(hashed_password):
        # Checking amount of users
        username = input("Enter your username: ")
        school = input("Enter your school: ")
        first_name = input("Enter your first name: ")
        last_name = input("Enter your last name: ")
        if db.query(func.count(models.User.id)).scalar() > 5:
            print("You have reached the maximum number of users.")
            continue_signup = input(
                "Would you like to login instead? (yes/no)")
            if continue_signup.lower() == 'yes':
                login(db)
            return
        if db.query(models.User).filter(models.User.username == username).first():
            print("Username already in use.")
            continue_signup = input(
                "Would you like to login instead? (yes/no)")  # change
            if continue_signup.lower() == 'yes':
                login(db)
            return
        user_create = UserCreate(username=username, hashed_password=hashed_password,
                                 school=school, first_name=first_name, last_name=last_name)
        new_user = models.User(**user_create.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = UserInfo(id=new_user.id, username=new_user.username, school=new_user.school,
                        first_name=new_user.first_name, last_name=new_user.last_name)
        
        remainder = db.query(models.ProspectiveConnection).filter(models.ProspectiveConnection.first_name == first_name, models.ProspectiveConnection.last_name == last_name).first()
        if remainder:
            caller = db.query(models.User).filter(models.User.id == remainder.caller_id).first()
            print(f"Hi, {caller.first_name} {caller.last_name} was looking for you")
            friend = Friends(user_id=caller.id, friend_id=new_user.id)
            friendship = models.Friendship(**friend.dict())
            db.add(friendship)
            db.delete(remainder)
            db.commit()
        
        main_hub(user, db)

    else:

        continue_signup = input(
            "Password is invalid. Do you want to continue signup? (yes/no): ")
        if continue_signup.lower() == 'yes':
            signup(db)
        else:
            print("Signup cancelled.")
            return


def login(db):
    # Get user input
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    if not check_password(password):
        continue_signup = input(
            "Password is invalid. Do you want to continue login? (yes/no): ")
        if continue_signup.lower() == 'yes':
            login(db)
        else:
            print("Login cancelled.")
        return

    queryUser = db.query(models.User).filter(
        models.User.username == username).first()
    if queryUser is None:
        print("Sigh Up first")
        return
    elif queryUser.hashed_password != password:
        print("Password is incorrect")
        return
    print("Login successfuly")
    user = UserInfo(id=queryUser.id, username=queryUser.username, school=queryUser.school,
                    first_name=queryUser.first_name, last_name=queryUser.last_name)
    main_hub(user, db)


def post_a_job(userData: UserInfo, db):
    while True:
        try:
            title = input("Enter the title of the job: ")
            content = input("Enter the content of the job: ")
            post = models.Post(title=title, content=content,
                               user_id=userData.id)
            db.add(post)
            db.commit()
            print("Job posted", "\n")
            print("do you want to post another job? (yes/no)")
            choice = input("Enter your choice: ")
            if choice.lower() == 'no':
                main_hub(userData, db)
                return

        except SQLAlchemyError:
            print("Error posting job")
            choice = input(
                "Would you like to go back to the main hub? (yes/no): ")

            if choice.lower() == 'yes':
                main_hub(userData, db)
            else:
                print("Re-enter details", "\n")


def main_hub(userData: UserInfo, db):

    print("Search for a job: (s) ")
    print("Find new friends: (nf)")
    print("Search a person by first and last name: (sp)")
    print("Learn new skills: (l)")
    print("View all friends: (vf)")
    print("Logout: (lo)")
    print("Job search and Internships: (p)")
    print("Exit: (e)")
    choice = input("Enter your choice: ")
    choice = choice.lower()
    if choice == 's':
        # search_job(userData, db)
        pass
    elif choice == 'nf':
        find_new_friends(userData, db)
    elif choice == 'l':
        learn_new_skills(userData, db)
    elif choice == 'vf':
        view_all_friends(userData, db)
    elif choice == 'lo':
        login(db)
    elif choice == 'p':
        post_a_job(userData, db)
    elif choice == 'sp':
        first_name = input("Enter the first name of the user: ")
        last_name = input("Enter the last name of the user: ")
        find_user_by_first_last_name_login(first_name, last_name, userData, db)

    elif choice == 'e':
        print("Goodbye")
        return
    else:
        print("Invalid choice")
        main_hub(userData, db)


# Fix it so it does not comeback to the main hub once user does not have friends
def view_all_friends(userData: UserInfo, db):

    friends = db.query(models.Friendship).filter(or_(models.Friendship.user_id == userData.id,
                                                     models.Friendship.friend_id == userData.id)).all()

    if not friends:
        print("You have no friends")
        main_hub(userData, db)
        return

    for index in friends:

        friend = db.query(models.User).filter(
            models.User.id == (index.friend_id)).first()
        if friend.id == userData.id:

            friend = db.query(models.User).filter(
                models.User.id == (index.user_id)).first()

        else:
            friend = db.query(models.User).filter(
                models.User.id == (index.friend_id)).first()

        print(
            f'Fisrt name: {friend.first_name}, last name: {friend.last_name}, school: {friend.school}, id: {friend.id}')
    choice = input("Would you like to go back to the main hub? (yes/no): ")
    if choice.lower() == 'yes':
        main_hub(userData, db)
    else:
        print("Goodbye")
        return


def find_new_friends(userData: UserInfo, db):
    users = db.query(models.User).all()
    idList = []
    for user in users:
        if user.id == userData.id:
            continue
        else:
            print(
                f"Username: {user.username}, First name: {user.first_name}, Last Name: {user.last_name}, School: {user.school}, ID: {user.id}")
            idList.append(user.id)
    add_friends(userData, db, idList)


def add_friends(userData: UserInfo,  db, idList: list):
    try:
        # Add try and Catch Block
        choice = int(
            input("if you want to add a friend, enter the id of the user, else enter no "))
        if choice not in idList:
            print("Invalid id")
        elif choice == userData.id:
            print("You cannot add yourself as a friend")
        elif (db.query(models.Friendship).filter(models.Friendship.user_id == userData.id, models.Friendship.friend_id == choice).first()
              or
              db.query(models.Friendship).filter(models.Friendship.user_id == choice, models.Friendship.friend_id == userData.id).first()):
            print("Friend already added")

        else:
            friends = Friends(user_id=userData.id, friend_id=choice)
            friendship = models.Friendship(**friends.dict())
            db.add(friendship)
            db.commit()
            print("Friend added")

        choiceAgain = input(
            "Do you still want to add more friends? (yes/no): ")
        if choiceAgain.lower() == 'no':
            main_hub(userData, db)
        else:
            add_friends(userData, db, idList)

    except ValueError:
        main_hub(userData, db)


def learn_new_skills(userData: UserInfo, db):
    print("Learn new skills")
    print("1. Python")
    print("2. Java")
    print("3. C++")
    print("4. C#")
    print("5. JavaScript")
    input("Enter your choice: ")
    print("Under contruction")
    choice = input("Would you like to go back to the main hub? (yes/no): ")
    if choice.lower() == 'yes':
        main_hub(userData, db)
    else:
        print("Goodbye")
        return


db = next(get_db())
try:
    signup(db)
finally:
    db.close()
