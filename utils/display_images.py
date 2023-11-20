import streamlit as st
import os

# augustinerplatz = r"./data/image_reimagined/AugustinerPlatz"
# marktstätte = r"./data/image_reimagined/Marktstätte"

# col1,col2 = st.columns(2)
# if "counter" not in st.session_state:
#     st.session_state.counter = 0
    
# def showPhoto(photo):
#     col2.image(photo,caption=photo)
#     col1.write(f"Index as a session_state attribute: {st.session_state.counter}")
    
#     ## Increments the counter to get next photo
#     st.session_state.counter += 1
#     if st.session_state.counter >= len(pathsImages):
#         st.session_state.counter = 0

# # Get list of images in folder
# folderWithImages = augustinerplatz
# pathsImages = [os.path.join(folderWithImages,f) for f in os.listdir(folderWithImages)]

# col1.subheader("List of images in folder")
# col1.write(pathsImages)