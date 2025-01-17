from google.cloud import firestore
import os
import base64
import json
import streamlit as st


@st.cache_resource
def get_firestore_db():
    json_content = decode_firestore_credentials()
    db = firestore.Client.from_service_account_info(json_content)
    return db


def load_conversation_by_id(cid):
    if cid and len(cid) > 0:
        db = get_firestore_db()
        return db.collection("conversations").document(cid).get()


def firestore_save(cid, conversation_record):
    db = get_firestore_db()
    if cid:
        # get conversation fromm cid
        conversation = db.collection("conversations").document(cid).get()
        # update conversation with the new messages and usage value
        conversation.reference.update(conversation_record)
        return conversation
    else:
        collection_ref = db.collection("conversations")
        # q: what does collection_ref.add(conversation_record) return and how do i get the id from the new record?
        # set created in conversation_record
        conversation_record["created"] = firestore.SERVER_TIMESTAMP
        _, record = collection_ref.add(conversation_record)
        return record


def decode_firestore_credentials():
    raw = os.environ["FIRESTORE_CREDENTIALS_BASE64"]
    # decode base64 string to json
    firebase_credentials = base64.b64decode(raw).decode("utf-8")
    json_data = json.loads(firebase_credentials)
    return json_data


def clear_user_history(uid):
    # delete all conversations that belong to the user
    db = get_firestore_db()
    conversations = db.collection("conversations").where("uid", "==", uid).stream()
    for c in conversations:
        c.reference.delete()
