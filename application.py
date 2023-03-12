import sys
import os
import csv
from PyQt5.QtWidgets import (QApplication,  QFileDialog)
from PyQt5 import QtWidgets
from modules import *
import time
from PyQt5.QtCore import QThread
from datetime import datetime
from PyQt5 import uic


Form, Window = uic.loadUiType("app_net_2.ui")


class ThreadClass(QThread):
    def __init__(self, directory, listWidget, listWidget_2):
        super().__init__()
        self.directory = directory
        self.listWidget = listWidget
        self.listWidget_2 = listWidget_2

    def run(self):
        if self.directory:
            is_running = False
            with open(self.directory[0], newline='') as File:
                try:
                    reader = csv.DictReader(File, delimiter=';')
                    is_running = True
                except:
                    self.terminate()

                if is_running:

                    self.listWidget.addItems(['Date | Host | RTT | PORTS | STATUS PORT'])
                    self.listWidget.addItems([''])

                    for id_row, row in enumerate(reader):
                        try:
                            host = row['Host']
                            ports = row['Ports']
                            data_process = DataProcessingAdapter(host, ports)
                            host, type_host, ports = data_process.processing()

                            check_server_get = CheckServerAdapter(host, type_host, ports)
                            work_server_get = WorkServerAdapter(host, ports)

                            if type_host == 'unknown':
                                if host == 'localhost':
                                    start = time.time()

                                    host = WorkServerAdapter(host, ports).get_ip_address_for_localhost()

                                    end = time.time()
                                    
                                    self.listWidget.addItems([f'Host: {host}:'])
                                    self.listWidget_2.addItems([f'Host: {host}:'])

                                    rtt = (end - start) * 1000
                                    ms = f'{rtt:.2f} ms'

                                    self.listWidget.addItems([datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f') + " | " +
                                                               host + " | " +
                                                               ms + " | " +
                                                               '???' + " | " +
                                                               '???'
                                                               ])

                            elif type_host == 'domaine':
                                ip_addresses, out_dns = work_server_get.get_ip_addresses_from_dns()

                                self.listWidget.addItems([f'Host: {host}:'])
                                self.listWidget_2.addItems([f'Host: {host}:'])

                                if ports:
                                    lst_ip_port_res = CheckServerAdapter(ip_addresses, type_host, ports).is_port_open()

                                    for inf_ip_add in lst_ip_port_res:
                                        ip, port, res, ms = inf_ip_add

                                        host = '???' if not ip else ip
                                        status = 'opened' if res else 'unknown'

                                        if port is not None:
                                            self.listWidget.addItems([datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f') + " | " +
                                                                       host + " | " +
                                                                       ms + " | " +
                                                                       str(port) + " | " +
                                                                       status
                                                                       ])
                                else:
                                    if len(ip_addresses) > 0:
                                        for ip_address in ip_addresses:
                                            start = time.time()

                                            out_ping = CheckServerAdapter(ip_address, type_host, ports).ping()

                                            end = time.time()

                                            rtt = (end - start) * 1000
                                            ms = f'{rtt:.2f} ms'

                                            self.listWidget_2.addItems([out_ping])

                                            self.listWidget.addItems([datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f') + " | " +
                                                                       ip_address + " | " +
                                                                       ms + " | " +
                                                                       '???' + " | " +
                                                                       '???'
                                                                       ])

                                    else:
                                        self.listWidget_2.addItems([out_dns])
                                        # print(out_dns)

                                out_server = check_server_get.get_is_working_server()
                                out_server_overload = check_server_get.get_server_overload()

                                if out_server is not None:
                                    self.listWidget_2.addItems([out_server])
                                else:
                                    self.listWidget_2.addItems(['Ошибка в работе сервера или некорректны данные'])
                                    # print('Ошибка в работе сервера или некорректны данные')

                                if out_server_overload == 'ошибка':
                                    self.listWidget_2.addItems(['Некорректные данные'])
                                    # print('Некорректные данные')
                                elif not out_server_overload:
                                    self.listWidget_2.addItems(['Сервер перегружен'])
                                    # print('Сервер перегружен')

                            elif type_host == 'ip_address':
                                self.listWidget.addItems([f'Host: {host}:'])
                                self.listWidget_2.addItems([f'Host: {host}:'])

                                if ports:
                                    lst_ip_port_res = check_server_get.is_port_open()
                                    for inf_ip_add in lst_ip_port_res:
                                        ip, port, res, ms = inf_ip_add

                                        status = 'opened' if res else 'unknown'

                                        if port is not None:
                                            self.listWidget.addItems([datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f') + " | " +
                                                                       str(ip) + " | " +
                                                                       ms + " | " +
                                                                       str(port) + " | " +
                                                                       status
                                                                       ])
                                else:
                                    start = time.time()

                                    out_ping = check_server_get.ping()

                                    end = time.time()

                                    rtt = (end - start) * 1000
                                    ms = f'{rtt:.2f} ms'

                                    self.listWidget_2.addItems([out_ping])

                                    self.listWidget.addItems([datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f') + " | " +
                                                               ip_address + " | " +
                                                               ms + " | " +
                                                               '???' + " | " +
                                                               '???'
                                                               ])

                            elif type_host == 'url':
                                host, port = work_server_get.get_port_and_host_from_url()

                                self.listWidget.addItems([f'Host: {host}:'])
                                self.listWidget_2.addItems([f'Host: {host}:'])

                                ports = set(ports + [80, 443] + [port])

                                if ports:

                                    lst_ip_port_res = CheckServerAdapter(host, type_host, ports).is_port_open()
                                    for inf_ip_add in lst_ip_port_res:
                                        ip, port, res, ms = inf_ip_add

                                        if port is not None:
                                            status = 'opened' if res else 'unknown'
                                            self.listWidget.addItems([datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f') + " | " +
                                                                       str(ip) + " | " +
                                                                       ms + " | " +
                                                                       str(port) + " | " +
                                                                       status
                                                                       ])
                                else:
                                    start = time.time()

                                    out_ping = check_server_get.ping()

                                    end = time.time()

                                    rtt = (end - start) * 1000
                                    ms = f'{rtt:.2f} ms'
                                    
                                    self.listWidget_2.addItems([out_ping])

                                    self.listWidget.addItems([datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f') + " | " +
                                                               ip_address + " | " +
                                                               ms + " | " +
                                                               '???' + " | " +
                                                               '???'
                                                               ])

                                out_server = check_server_get.get_is_working_server()
                                out_server_overload = check_server_get.get_server_overload()

                                if out_server is None:
                                    self.listWidget_2.addItems(['Ошибка в работе сервера или некорректны данные'])
                                    # print('Ошибка в работе сервера или некорректны данные')

                                if out_server_overload == 'ошибка':
                                    self.listWidget_2.addItems(['Некорректные данные'])
                                    # print('Некорректные данные')

                                elif not out_server_overload:
                                    self.listWidget_2.addItems(['Сервер перегружен'])
                                    # print('Сервер перегружен')

                            else:
                                self.listWidget_2.addItems([f'Host: {host}:'])
                                self.listWidget_2.addItems(['Некорректные данные или ошибка серверного приложения'])
                                # print('Некорректные данные или ошибка серверного приложения')
                            self.listWidget.addItems([''])
                            self.listWidget_2.addItems([''])
                        except:
                            pass


class Ui(QtWidgets.QDialog, Form):
    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Мониторинг работоспособности серверов')
        self.setFixedSize(1104, 632)

        self.pushButton.clicked.connect(self.getFileNames)
        self.pushButton_2.clicked.connect(self.clear_output)
        self.pushButton_3.clicked.connect(self.stop_or_continue_process)
        self.pushButton_3.setEnabled(False)

    def getFileNames(self):
        file_filter = 'Files (*.csv);'
        response = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Выберите файл',
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter='Csv File (*.csv)'
        )
        if response[0]:
            self.label_2.setText(f"Загруженный файл: {os.path.basename(response[0][0]).split('.')[0]}")
            self.label_2.resize(180, 30)
            self.label_2.setStyleSheet("color: #008000; ")
            self.threadclass = ThreadClass(response[0], self.listWidget, self.listWidget_2)
            self.pushButton_3.setEnabled(True)
            self.threadclass.start()

    def clear_output(self):
        self.listWidget.clear()
        self.listWidget_2.clear()

    def closeEvent(self, event):
        try:
            self.threadclass.terminate()
        except:
            pass

        event.accept()

    def stop_or_continue_process(self):
        self.threadclass.terminate()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Ui()
    ex.show()
    sys.exit(app.exec())
