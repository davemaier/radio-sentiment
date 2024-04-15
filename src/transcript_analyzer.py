import marimo

__generated_with = "0.3.12"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    from openai import OpenAI
    return OpenAI, mo


@app.cell
def __(mo):
    mo.md(
    """
    # Transcript analysis

    This script can be used to analyze a transcript of a radioshow (or any other text). It uses **OpenAIs GPT4-turbo** model via the provides API. To make communication with the API more compfortable, we use the official OpenAI Python SDK. 
    """
    )
    return


@app.cell
def __():
    import subprocess
    import httpx
    import time
    from datetime import datetime
    import threading
    return datetime, httpx, subprocess, threading, time


@app.cell
def __(httpx, mo):
    _r = httpx.get("http://de1.api.radio-browser.info/json/stations/bycountryexact/austria")

    # Initialize an empty dictionary to store label-URL pairs
    label_url_dict = {}

    # Loop through each item in the JSON list
    for item in _r.json():
      # Extract the label and URL from the item
      label = item["name"]
      url = item["url"]

      # Add the label-URL pair to the dictionary
      # Use setdefault to avoid overwriting existing keys with the same label
      label_url_dict[label] = url.strip()  # Optional: strip leading/trailing whitespaces

    inv_label_url_dict = {v: k for k, v in label_url_dict.items()}

    stationA = mo.ui.dropdown(options=label_url_dict, label='Select a station A')
    stationB = mo.ui.dropdown(options=label_url_dict, label='Select a station B')

    start_date = mo.ui.date()
    start_hours = mo.ui.number(start=0, stop=23, step=1)
    start_min = mo.ui.number(start=0, stop=59, step=1)

    duration_hours = mo.ui.number(start=0, stop=23, step=1)
    duration_min = mo.ui.number(start=0, stop=59, step=1)
    duration_sec = mo.ui.number(start=0, stop=59, step=1)

    def btn_activate_onclick(value):
        if value == "inactive":
            return "active"
        elif value == "active":
            return "inactive"


    btn_activate = mo.ui.button(
        label="Activate/Stop", 
        value="inactive",
        on_click=btn_activate_onclick)
    return (
        btn_activate,
        btn_activate_onclick,
        duration_hours,
        duration_min,
        duration_sec,
        inv_label_url_dict,
        item,
        label,
        label_url_dict,
        start_date,
        start_hours,
        start_min,
        stationA,
        stationB,
        url,
    )


@app.cell(hide_code=True)
def __(
    btn_activate,
    duration_hours,
    duration_min,
    duration_sec,
    mo,
    start_date,
    start_hours,
    start_min,
    stationA,
    stationB,
):
    mo.md(f"""
    {stationA} \n
    {stationB} \n
    Start date: {start_date} \n
    Start time: {start_hours} : {start_min} \n
    Duration: {duration_hours} hours {duration_min} min  {duration_sec} sec\n
    {btn_activate}
    """)
    return


@app.cell
def __(btn_activate, mo, recording_state):
    mo.md(f"Current Status: {btn_activate.value} Recording state: {recording_state}")
    return


@app.cell
def __(
    btn_activate,
    duration_hours,
    duration_min,
    duration_sec,
    httpx,
    inv_label_url_dict,
    time,
):
    def record_radio(station):
        print(station.value)
        start_time = time.time()
        
        with open(f"recording_{time.strftime("%Y%m%d%H%M%S")}_{inv_label_url_dict[station.value]}.mp3", "wb") as file:
            with httpx.stream('GET', station.value) as r:
                recording_state = "recording"
                for data in r.iter_bytes():
                    elapsed_time = time.time() - start_time
                    if btn_activate.value != "active" or elapsed_time > (duration_hours.value * 60 + duration_min.value) * 60 + duration_sec.value:
                        break
                    file.write(data)
    return record_radio,


@app.cell
def __(
    btn_activate,
    datetime,
    record_radio,
    start_date,
    start_hours,
    start_min,
    stationA,
    stationB,
    threading,
    time,
):
    target_datetime = datetime(year=start_date.value.year, month=start_date.value.month, day=start_date.value.day, hour=start_hours.value, minute=start_min.value)
    recording_state = "initial"

    if btn_activate.value == "active":
        recording_state = "waiting for start time"
        while btn_activate.value == "active":  
          if datetime.now() >= target_datetime:
            print("recording")
            thread_stationA = threading.Thread(target=record_radio, args=(stationA,))
            thread_stationB = threading.Thread(target=record_radio, args=(stationB,))

            thread_stationA.start()
            thread_stationB.start()
              
            thread_stationA.join()
            thread_stationB.join()
              
            recording_state = "finished"
            break  
          time.sleep(1)
    return (
        recording_state,
        target_datetime,
        thread_stationA,
        thread_stationB,
    )


@app.cell
def __(mo):
    mo.md("""
    # Transcribe using whisper
    Now we can use the recorded radio program to create a transcript using OpenAI whisper.
    We use the CLI program `insanely-fast-whisper` for this task, because it is easier to use than most other open source solutions and works sufficiently well on Mac. Most other solution are only preconfigured to be used with a CUDA enabled GPU. 

    **TODO: IMPLEMENT TRANSCRIPTION**
    """)
    return


@app.cell
def __(OpenAI):
    client = OpenAI(
      organization='org-wTkHlf3xgp0VhSI8oNBaLSqO'
    )
    return client,


@app.cell
def __(client):
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={ "type": "json_object" },
        messages=[
        {"role": "system", "content": """
        You are a specialist on environmental topics. 
        You know everything about environmentally adverse advertising and environmental sentiment in media. 
        You help me to analyze transcripts of radio programms. 
        Doing so, you identify every advertisment in the transcript, extract information about the product and the company of the ad.
        You also rank the environmental adversity of the add on a scale between 1 and 5 and add the cause for your decision.
        Your answer should be valid JSON in the following format:
        {
        "ads": [
        {
        "id": "<int_incremental>",
        "product": "<string_product_name>",
        "company": "<string_company_name>",
        "adversity": "<int>",
        "cause": "<string_cause>"
        }
        ],
        "total": "<int_total_ads>"
        }
        You answer only the JSON and nothing else. You don't return markdown but plain text. Your answers are in english.
        """},
        {"role": "user", "content": """
        Musik Untertitelung des ZDF, 2020 Mein große Tochter hat sogar in der Schule schon gehört, freut deine Mama eigentlich das Arbeiten nicht. Und das tut irgendwie voll weh, weil ich bin einfach total gern bei den Kindern daheim. Seit 45 Jahren bin ich in die Hauptschule gegangen und da war es für Burschen, die Wettbewerb zeichnen und für Mädchen kochen. Und ich bin bis zum Ministerium vorgegangen und dann ist das nachher eingesetzt worden für alle Schulen. Also man kann sich schon als Kinder ein bisschen wehren dagegen. Ich bin der Frust Andreas aus Schäuble-Hirsen. Ich möchte einfach noch einmal bedanken für meine Frau, die halt einfach die Alleinverdienerin ist und so im Prinzip auch die ganze Familie auf ihren Schultern dreht. Treffpunkt Klischee, der Weltfrauentag auf der 3. Untertitelung des ZDF für funk, 2017 Bis zum nächsten Mal. Untertitelung im Auftrag des ZDF für funk, 2017 Und das Gefühl geht weiter und weiter und weiter. Bis zum nächsten Mal. Diese Sendung enthielt Produktplatzierungen. Diese Sendung enthielt Produktplatzierungen. Grüß euch, da ist der Hans Knaus. Dass die Schweizer im Skifahren gut sind, das wissen wir eh wohl. Aber eines sage ich euch, beim Versichern sind es einfach klar die Besten. Das ist fix. Einfach. Klar. Helvetia. Ihre Schweizer Versicherung. Nur solange der Vorrat reicht. Kick, der Preis spricht für sich. Jetzt und nur für kurze Zeit bei McDonald's. Der Chicken Big Mac. Legendärer Geschmack trifft auf extra knuspriges Hühnerfleisch. I'm loving it. Die Designer-Outlets Pahndorf und Salzburg wünschen heute allen Frauen einen besonders schönen Tag und sagen einfach mal Danke. Lasst euch feiern, denn heute ist internationaler Frauentag. Wir bewundern euren Mut und Stärke und so vieles mehr. Ihr seid einfach großartig. Eure KollegInnen aus den Designer-Outlets Pahndorf und Salzburg. Bei Kika-Liner gibt's nicht nur alles zu Kika-günstigeren Preisen und kleiner besserem Service, sondern jetzt auch mit Gutschein auf fast alles die Mehrwertsteuer geschenkt. Entspricht einem Nachlass von 16,67 Prozent. Ausnahmen und Aktionsbedingungen auf Kika-T und Liner-T. Der neue Kika-Leiner. Kommt euch näher. 17 Mal in Österreich. Sie denken an ein neues Auto? Dann kommen Sie am 15. und 16. März zu Denzel. Das Autohaus mit der größten Markenvielfalt wird 90. Und das feiern wir mit den neuesten Modellen und tollen Aktionen. Die Denzel Days. 15. und 16. März an über 20 Denzel-Standorten in Österreich. Mehr auf Denzel Days. 15. und 16. März an über 20 Denzel-Standorten in Österreich. Mehr auf denzel.at Leben wie in den Geschichten aus Tausend und eine Jacht. Jetzt mehr als 60 Millionen Euro gewinnen. Euro-Millionen. Reicher als reich. Jetzt bei Billa unterm Strich günstiger aussteigen. Zum Beispiel mit den Rabattpickerln, dem Jürabatsammler und minus 25 Prozent auf das gesamte Kaffeesortiment. Nur diesen Freitag und Samstag. Details auf Billa.at. Hier ist die 3. In dieser Stunde gibt es die Lieblingssitz von Tate McRae, Fawn & Blondes und Emily Sondy. Jetzt zu Elise Pelzelmeier. Es ist 11 Uhr. Ö3 Nachrichten Das Landesgericht Innsbruck hat jetzt ein Konkursverfahren über das Vermögen des Signergründers René Benko eröffnet. Das Verfahren bezieht sich auf Benkos Beratungsunternehmen und dessen Privateigentum. Ö3-Reporter Volker Obermeier, für René Benko hat das jetzt Konsequenzen. Der Schuldner, also René Benko, muss die komplette Kontrolle und Verfügung in Bezug auf sein Vermögen im In- und Ausland abgeben. Nun ist genau das eingetreten, was die Finanzprokuratur, der Anwalt der Republik, erreichen wollte, die völlige Offenlegung der Besitzverhältnisse. Der Insolvenzverwalter steht nun vor einer Mammutaufgabe. Erstens ist die Höhe der Verbindlichkeiten noch nicht klar. Zweitens muss er sich durch sämtliche Vermögenstransaktionen der vergangenen zehn Jahre arbeiten, um Ansprüche von Gläubigern feststellen zu können. In diesen Minuten beginnt im Bundeskanzleramt eine Pressekonferenz mit Bundeskanzler Karl Nehammer. Es wird dort offenbar der Rücktritt von Digitalisierung-staatssekretär Florian Turski verkündet. Das berichtet die Austria-Presseagentur. Turski will ja Bürgermeister in Innsbruck werden. Er tritt bei der Gemeinderatswahl am 14. April für die Liste das neue Innsbruck an. Darauf wolle er sich jetzt ganz konzentrieren, berichtet die APA. Zu 15 Monaten teilbedingter Haft ist gestern jene Frau verurteilt worden, deren Hunde eine Joggerin in Nahen im Bezirk Perg totgebissen haben. Das Urteil ist bereits rechtskräftig. Ob die 38-Jährige wirklich ins Gefängnis muss, ist noch offen. Ihr Verteidiger Philipp Wohlmacher hofft auf Hausarrest mit Fußfessel. Ein Fußfessel hat grundsätzlich die rechtliche Möglichkeit bei einer restlich verbleibenden, zu verbüßenden Freiheitsstrafe von zwölf Monaten. Und daher ist ein Fußfessel natürliche Option. In eine Schule bei Berlin ist heute früh ein 22-Jähriger Bewaffneter eingedrungen. Der Mann hat ein Messer und eine Schreckschusswaffe bei sich gehabt. Die Polizei hat ihn kurz danach festgenommen. Bei der Festnahme sind der Angreifer und ein Polizist leicht verletzt worden. Zum Motiv des 22-Jährigen hat sich die Polizei noch nicht geäußert. Und millionenschwerer Kunstdiebstahl am Gardasee. Aus einem Museum in Gardone Riviera sind sämtliche Kunstwerke einer Ausstellung gestohlen worden. Es handelt sich um 49 Schmuckstücke und Skulpturen aus Gold. Die Ermittler gehen von einer Profibande aus, die den Coup bis ins Detail geplant hat. Die Alarmanlage war aktiv, ist jedoch nicht ausgelöst worden. Jetzt zum Wetter mit Nicola Biermeier. Leicht föhniger Südwind teilt Österreich in drei Wetterbereiche heute. Sonnig und mild haben sie es vom Rheintal bis ins Mostviertel. Nebel am Bodensee oder um Vöcklerbruck löst sich auf und die Temperaturen reichen 9 bis 14 Grad. Ein bisschen Sonne lassen Nebel und Hochnebel allmählich auch in Niederösterreich, Wien und dem Burgenland durch bei Werten um 8 Grad. In Osttirol, in Kärnten, dem Lungau und weiten Teilen der Steiermark bleibt es hingegen kühl, teilweise nur 4 Grad und bewölkt. Hier regnet oder schneit es auch ein bisschen. Am Wochenende ähnlich, aber etwas mehr Wolken. Föhn und Temperaturen legen noch zu. Am Sonntag sind vereinzelt 18 Grad möglich. Kurz nach 11 Uhr der schnellste Verkehrsservice Österreichs auf Ö3. Mit Klaus Gesselbauer und bitte vorwärts.
        """
        },
        ]
    )
    return response,


@app.cell
def __(response):
    print(response.choices[0].message)
    return


if __name__ == "__main__":
    app.run()
