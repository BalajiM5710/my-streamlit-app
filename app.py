import streamlit as st
import os
import random
import pandas as pd
import hashlib

# Define the paths to the images directories
image_dirs = ["images1","images2"]

# Path to the CSV file that stores votes
votes_csv_path = 'votes.csv'

# Load existing votes
if os.path.exists(votes_csv_path):
    votes_df = pd.read_csv(votes_csv_path)
    voted_images = set(votes_df['file_name'])
else:
    votes_df = pd.DataFrame(columns=['file_name', 'voted_emotion', 'voter_name'])
    voted_images = set()

# Initialize session state to keep track of votes and user chunk assignment
if 'votes' not in st.session_state:
    st.session_state.votes = []
if 'user_chunk' not in st.session_state:
    st.session_state.user_chunk = None

# List all images in the directories
image_files = []
for image_dir in image_dirs:
    image_files.extend([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif'))])

# Split images into chunks
num_chunks = 5
chunks = [image_files[i::num_chunks] for i in range(num_chunks)]

# Function to get the chunk index for a user
def get_chunk_index(username):
    return int(hashlib.md5(username.encode()).hexdigest(), 16) % num_chunks

# Input for the user's name
username = st.text_input("Enter your name:")
if username:
    session_id = username
    session_state = st.session_state.get(session_id, {})
    if 'user_chunk' not in session_state:
        chunk_index = get_chunk_index(username)
        session_state['user_chunk'] = chunks[chunk_index]
    st.session_state[session_id] = session_state
    
    # Filter out images that have already been voted on by this user
    unseen_images = [img for img in session_state['user_chunk'] if img not in voted_images]

    # Calculate the user's progress
    total_images_user = len(session_state['user_chunk'])
    voted_images_user_count = total_images_user - len(unseen_images)
    user_progress = voted_images_user_count / total_images_user

    # Calculate the overall progress
    total_images = len(image_files)
    voted_images_count = len(voted_images)
    overall_progress = voted_images_count / total_images

    # Display the progress bars
    st.write("Your Progress")
    st.progress(user_progress)
    st.write(f"{voted_images_user_count}/{total_images_user} images have been voted on.")
    
    st.write("Overall Progress")
    st.progress(overall_progress)
    st.write(f"{voted_images_count}/{total_images} images have been voted on.")

    # If all images have been seen by this user, show a completion message
    if not unseen_images:
        st.write("You have voted on all your images!")
    else:
        # Randomly select an image from the unseen images
        current_image = random.choice(unseen_images)
        
        # Display the image
        st.image(current_image, use_column_width=True)
        
        # Define the voting function
        def vote(emotion):
            # Add the vote to the session state
            vote_info = (current_image, emotion, username)
            votes_df.loc[len(votes_df)] = vote_info
            votes_df.to_csv(votes_csv_path, index=False)
            # Clear the current votes from session state
            st.experimental_rerun()

        # Display voting buttons
        st.button('Happy', on_click=vote, args=('happy',))
        st.button('Sad', on_click=vote, args=('sad',))
        st.button('Neutral', on_click=vote, args=('neutral',))
        st.button('Angry', on_click=vote, args=('angry',))

    # If all images have been voted on by all users, provide a download link for the CSV
    if overall_progress == 1.0:
        st.write("All images have been voted on by all users!")
        csv = votes_df.to_csv(index=False)
        st.download_button(label="Download Votes CSV", data=csv, file_name="votes.csv", mime="text/csv")
else:
    st.write("Please enter your name to start voting.")
