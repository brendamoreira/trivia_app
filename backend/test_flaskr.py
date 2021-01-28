import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.question = Question(question='new question', answer='answer fake', difficulty=1, category='category')
        self.question.insert()

    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            self.db.session.query(Question).delete()
            self.db.session.commit()


    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories_list(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_categories'], 0)
        self.assertEqual(len(data['categories']), 0)
    
    def test_get_questions_list(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_questions'], Question.query.count())
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_question_delete(self):
        id = self.question.id
        res = self.client().delete(f'/questions/{self.question.id}')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(Question.query.filter(Question.id == id).one_or_none(), None)

    def test_404_delete_if_doesnt_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_question(self):
        res = self.client().post('/questions', json=self.question.format())
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post('/questions/1000', json=self.question.format())
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()