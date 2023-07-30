# first line: 15
@memory.cache
def calc_similarity(user_question, question):
    embeddings_user_question = model.encode(user_question, convert_to_tensor=True)
    embeddings_question = model.encode(question, convert_to_tensor=True)
    return util.pytorch_cos_sim(embeddings_user_question, embeddings_question)[0, 0]
