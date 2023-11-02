import re
import time
import joblib
import numpy as np
import pandas as pd
import streamlit as st


def main():
	st.set_page_config(
	    page_title="Password Strength",
	    # page_icon=favicon,
	    initial_sidebar_state="expanded",
	)

	st.markdown(
	    f'''
	        <style>
	        	.reportview-container .main .block-container{{
			        padding-top: {2}rem;
			        padding-right: {5}rem;
			        padding-left: {5}rem;
			        padding-bottom: {3}rem;
			    }}

	            .sidebar .sidebar-content {{
	                width: 375px;
	            }}
	        </style>
	    ''',
	    unsafe_allow_html=True
	)

	# st.image('expresso_logo.png', width=100)
	st.title('PASSWORD STRENGTH CLASSIFIER')
	st.subheader("""
		Enter your password and it will be predicted if weak, medium or strong
		""")
	st.markdown(
	    '<hr/>',
	    unsafe_allow_html=True
	)

	# Load model
	model = joblib.load('model.joblib')

	# Feature Engineering for user inputs

	# Character count features
	password_length = lambda password: len(password)
	password_has_lowercase = lambda password: 1 if any(char.isupper() for char in password) else 0
	password_has_uppercase = lambda password: 1 if any(char.isupper() for char in password) else 0
	password_has_number = lambda password: 1 if any(char.isdigit() for char in password) else 0
	password_has_special_char = lambda password: 1 if (pd.notna(password) and re.search(r'[!@#$%^&*(),.?":{}|<>]', password)) else 0
	password_uppercase_count = lambda password: sum(1 for char in password if char.isupper())
	password_lowercase_count = lambda password: sum(1 for char in password if char.islower())
	password_digit_count = lambda password: sum(1 for char in password if char.isdigit())
	password_special_char_count = lambda password: len([char for char in password if not char.isalnum()])


	# Sequential character features
	password_consecutive_upper = lambda password: max((len(run) for run in password.split() if run.isupper()), default=0)
	password_consecutive_lower = lambda password: max((len(run) for run in password.split() if run.islower()), default=0)
	password_consecutive_digits = lambda password: max((len(run) for run in password.split() if run.isdigit()), default=0)

	# feature using the entropy score
	def calculate_entropy(password):
		char_count = len(password)
		if char_count == 0:
			return 0.0
		else:
			char_set = set(password)
			entropy_score = -sum((password.count(char) / char_count) * np.log2(password.count(char) / char_count) for char in char_set)
			return entropy_score

	with st.form(key='password_check_form'):
		user_input = st.text_input('Password', key='password_input')
		if st.form_submit_button('Check'):
			with st.spinner('Classifying, please wait...'):

				# Perform feature engineering
				length = password_length(user_input)
				has_uppercase = password_has_uppercase(user_input)
				has_lowercase = password_has_lowercase(user_input)
				has_number = password_has_number(user_input)
				has_special_char = password_has_special_char(user_input)
				uppercase_count = password_uppercase_count(user_input)
				lowercase_count = password_lowercase_count(user_input)
				digit_count = password_digit_count(user_input)
				special_char_count = password_special_char_count(user_input)
				consecutive_upper = password_consecutive_upper(user_input)
				consecutive_lower = password_consecutive_lower(user_input)
				consecutive_digits = password_consecutive_digits(user_input)
				entropy = calculate_entropy(user_input)

				feature_vector = [
					length, has_uppercase, has_lowercase, has_number, has_special_char, 
					uppercase_count, lowercase_count, digit_count, special_char_count, 
					consecutive_upper, consecutive_lower, consecutive_digits, entropy
				]

				time.sleep(3)
				# Make prediction
				prediction = model.predict([feature_vector])
			st.success('Done!')

			strength = "Weak" if prediction == 0 else "Medium" if prediction == 1 else "Strong" if prediction == 2 else "Strong"
			st.write(f'Password strength: {strength}')


if __name__ == "__main__":
	main()


