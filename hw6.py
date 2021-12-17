#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
import os.path
import sqlite3
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Text)
    education = db.Column(db.Text)
    age = db.Column(db.Integer)

    
class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Text, primary_key=True)
    text = db.Column(db.Text)

    
class Answers(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, ForeignKey('questions.id'), primary_key=True)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)
    q3 = db.Column(db.Integer)
    q4 = db.Column(db.Integer)
    q5 = db.Column(db.Integer)
    q6 = db.Column(db.Integer)

    
db.create_all()


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/questionnaire')
def question_page():
    questions_1 = Questions.query.all()[0:3]
    questions_2 = Questions.query.all()[3:]
    return render_template(
        'form.html',
        questions_1=questions_1, questions_2=questions_2
    )


@app.route('/process', methods=['get'])
def answer_process():
    if not request.args:
        return redirect(url_for('question_page'))
    gender = request.args.get('gender')
    education = request.args.get('education')
    age = request.args.get('age')
    user = User(
        age=age,
        gender=gender,
        education=education
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    q1 = request.args.get('q1')
    q2 = request.args.get('q2')
    q3 = request.args.get('q3')
    q4 = request.args.get('q4')
    q5 = request.args.get('q5')
    q6 = request.args.get('q6')
    answer = Answers(id=user.id, q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6)
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('thanking'))


@app.route('/thanks')
def thanking():
    return render_template('thanks.html')


@app.route('/stats')
def stats():
    all_info = {}
    age_stats = db.session.query(
        func.avg(User.age),
        func.min(User.age),
        func.max(User.age)
    ).one()
    all_info['age_mean'] = round(age_stats[0], 2)
    all_info['age_min'] = age_stats[1]
    all_info['age_max'] = age_stats[2]
    all_info['q1_mean'] = round(db.session.query(func.avg(Answers.q1)).one()[0], 2)
    all_info['q2_mean'] = round(db.session.query(func.avg(Answers.q2)).one()[0], 2)
    all_info['q3_mean'] = round(db.session.query(func.avg(Answers.q3)).one()[0], 2)
    all_info['q4_mean'] = round(db.session.query(func.avg(Answers.q6)).filter(Answers.q1 + Answers.q2 >= 8).one()[0], 2)
    all_info['q5_mean'] = round(db.session.query(func.avg(Answers.q4)).filter(Answers.q3 > 3).one()[0], 2)
    all_info['q6_mean'] = round(db.session.query(func.avg(Answers.q5)).filter(Answers.q3 > 3).one()[0], 2)
    return render_template('results.html', all_info=all_info)


if __name__ == '__main__':
    app.run(debug=False)

