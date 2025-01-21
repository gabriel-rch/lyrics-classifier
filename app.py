import gradio as gr
import joblib


pipeline = joblib.load("pipeline.pkl")


def classify_lyrics(lyrics):
    """Classify the genre of the given lyrics."""
    return pipeline.predict([lyrics])[0]


# Build Gradio interface
interface = gr.Interface(
    fn=classify_lyrics,
    inputs=gr.Textbox(label="Letra da Música", placeholder="Escreva suas letras aqui..."),
    outputs=gr.Label(label="Predição de Gênero"),
    allow_flagging="never",
    title="Classificador de Gênero de Músicas",
    description="Classifique o gênero de uma música com base em suas letras.",
    examples=[
        ["E nessa loucura de dizer que não te quero, vou negando as aparências, disfarçando as evidências"],
        ["Me arrastando de volta para você, Já pensou em ligar quando você toma umas? Porque eu sempre penso"],
        ["Porque Ele vive, posso crer no amanhã, Porque Ele vive, temor não há"],
        ["Tem hora dá vontade de bater no Piauí, Já puxei a rota, em oito horas tô chegando por aí"],
    ],
)

if __name__ == "__main__":
    interface.launch()
