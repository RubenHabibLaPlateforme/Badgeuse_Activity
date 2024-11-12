import threading
from controllers.ApiPlateforme import ApiPlateforme
from smartcard.System import readers
from smartcard.util import toHexString

# from controllers.App import App


class RfidReader:
    def start_rfid_thread(
        self, appInstance, part2_frame, canvas, part3_frame, data_badges, callback
    ):
        thread = threading.Thread(
            target=self.read_rfid,
            args=(part2_frame, canvas, part3_frame, data_badges, appInstance, callback),
        )

        thread.daemon = True
        thread.start()

    def read_rfid(
        self, part2_frame, canvas, part3_frame, data_badges, appInstance, callback
    ):
        print("Lecture en cours")
        while True:
            # print("READ RFID")
            card_id = 0

            # Recherche des lecteurs de cartes
            card_readers = readers()

            if len(card_readers) == 0:
                return

            reader = card_readers[0]

            try:
                connection = reader.createConnection()
                connection.connect()

                # Lire le numéro de série de la carte RFID
                READ_SERIAL = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                response, sw1, sw2 = connection.transmit(READ_SERIAL)
                if sw1 == 0x90 and sw2 == 0x00:
                    response_reversed = response[::-1]

                    card_id = int(toHexString(response_reversed).replace(" ", ""), 16)

                    student_email = ApiPlateforme.get_student_by_badge(
                        data_badges, card_id
                    )
                    # print("Email student " + student_email)
                    if student_email:
                        callback(student_email, True)
                        print(student_email)
                        # -1,
            except Exception as e:
                pass

            finally:
                connection.disconnect()

    # root.after(10000, read_rfid, root)
