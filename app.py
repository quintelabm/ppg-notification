from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
from ics import Calendar, Event
import io

app = Flask(__name__)

# Regras de prazos por curso (em meses)
DEADLINES = {
    "mestrado": {
        "Escolha de Orientador": 3,
        "Envio da Proposta de Dissertação": 9,
        "Envio da Proficiência": 12,
        "Integralizaçao de creditos para Estágio Docência": 18,
        "Indicação de Coorientador": 18,
        "Defesa da Dissertação": 24,
    },
    "doutorado": {
        "Escolha de Orientador": 3,
        "Qualificação": 24,
        "Estagio Docencia I": 24,
        "Proficiência em inglês": 24,
        "Proficiência em Segunda Língua": 36,
        "Estagio Docencia II": 36,
        "Seminario de acompanhamento": 48,
        "Defesa da Tese": 48,
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data_ingresso_str = request.form["data_ingresso"]
        curso = request.form["curso"]

        if curso not in DEADLINES:
            return "Curso inválido.", 400

        data_ingresso = datetime.strptime(data_ingresso_str, "%Y-%m-%d")

        # Criar calendário
        calendar = Calendar()

        for evento, meses in DEADLINES[curso].items():
            data_evento = data_ingresso + timedelta(days=meses*30)  # Aproximação
            e = Event()
            e.name = f"[{curso.upper()}] {evento}"
            e.begin = data_evento
            e.description = f"Lembrete: {evento.lower()} (prazo aproximado de {meses} meses após ingresso)."
            e.make_all_day()
            calendar.events.add(e)

        # Gerar arquivo ICS
        buffer = io.StringIO(str(calendar))
        byte_io = io.BytesIO()
        byte_io.write(buffer.getvalue().encode("utf-8"))
        byte_io.seek(0)

        return send_file(
            byte_io,
            as_attachment=True,
            download_name=f"lembretes_{curso}.ics",
            mimetype="text/calendar"
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
