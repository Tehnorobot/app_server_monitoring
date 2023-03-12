import csv
import re
import socket
import platform
import subprocess
import requests
from urllib.parse import urlparse
import time

'''Пример модуля для замены'''


class NewModule:
    # Пример архитектуры модуля, который можно заменить
    # в соостветствующем адаптере. `self.module = NewModule()
    def __init__(self):
        pass

    def get_is_working_server(self, host, type_host):
        pass

    def ping(self, host):  # Проверка домена на доступность через ping
        pass


'''Класс обработки данных'''


class DataProcessing:
    def processing(self, host, ports):
        preprocess_host = host.lower().strip()
        preprocess_port = ports.lower().strip()

        if not (
            len(preprocess_port) > 0 and
            re.fullmatch("^\d+(\,\d+)*$", preprocess_port)
        ):  # Проверка, что port состоит только из цифр и длина > 0
            preprocess_ports = []
        else:
            preprocess_ports = list(map(int, preprocess_port.split(",")))

        if len(preprocess_host) > 0:  # Проверка, что длина host > 0
            if re.fullmatch(
                "^\d+.\d+.\d+.\d+", preprocess_host
            ):  # Проверка, что host соответствует
            # маске "число.число.число.число"
                return (
                    preprocess_host,
                    "ip_address",
                    preprocess_ports,
                )  # Вывод host, тип host
            # (ip_address, domaine, url или unknown), port

            elif re.fullmatch(
                "^[a-zA-Zа-яА-Я0-9]+\.[a-zA-Zа-яА-Я0-9]+$", preprocess_host
            ):  # Проверка, что host соответствует
            # маске "число/буквы.число/буквы"
                return (
                    preprocess_host,
                    "domaine",
                    preprocess_ports,
                )  # Вывод host, тип host
            # (ip_address, domaine, url или unknown), port

            elif re.fullmatch(
                "^http[s]*:\/\/[a-zA-Zа-яА-Я0-9]+\.[a-zA-Zа-яА-Я0-9]+\.[a-zA-Zа-яА-Я00-9]+.*",
                preprocess_host,
            ):  # Проверка, что host является url
                return (
                    preprocess_host,
                    "url",
                    preprocess_ports,
                )  # Вывод host, тип host
            # (ip_address, domaine, url или unknown), port

            else:
                return (
                    preprocess_host,
                    "unknown",
                    preprocess_ports,
                )  # Вывод host, тип host
            # (ip_address, domaine, url или unknown), port

        else:
            # Вывод None и port, если есть только port
            return None, "unknown", preprocess_ports


class DataProcessingAdapter:
    def __init__(self, host, ports):
        self.host = host
        self.ports = ports
        self.module = DataProcessing()

    def processing(self):
        return self.module.processing(self.host, self.ports)

    def get_host(self):
        return self.host

    def get_ports(self):
        return self.ports


'''Класс работы с сервером'''


class WorkServer:
    def get_ip_address_for_localhost(self):
        # получить ip-адресс localhost
        socket.setdefaulttimeout(1)
        return socket.gethostbyname('localhost')

    def get_ip_addresses_from_dns(self, host):
        # получить ip-адреса от dns
        ip_addresses = set()
        try:
            for addr_info in socket.getaddrinfo(host, None):
                ip_addresses.add(addr_info[4][0])

            return ip_addresses, 'успешно'
        except socket.error:
            return (ip_addresses,
                    'DNS сервер не возвращает IP-адрес по доменному имени')

    def get_port_and_host_from_url(self, url):  # Получить домен и порт по url
        parsed_url = urlparse(url)

        ip = parsed_url.hostname  # извлечение ip-адреса
        port = parsed_url.port

        return ip, port


class WorkServerAdapter:
    def __init__(self, host, ports):
        self.host = host
        self.ports = ports
        self.module = WorkServer()

    def get_ip_address_for_localhost(self):
        # получить ip-адресс localhost
        return self.module.get_ip_address_for_localhost()

    def get_ip_addresses_from_dns(self):
        # получить ip-адреса от dns
        return self.module.get_ip_addresses_from_dns(self.host)

    def get_port_and_host_from_url(self):  # Получить домен и порт по url
        return self.module.get_port_and_host_from_url(self.host)

    def get_host(self):
        return self.host

    def get_ports(self):
        return self.ports


'''Класс проверки работы сервера'''


class CheckServer:
    def __init__(self):
        self.dict_out_code_ping = {
            0: 'успешный запрос',
            1: 'аппаратная ошибка или транспортный уровень или сеть недоступны',
            2: 'некорректный синтаксис команды Ping',
            3: 'адрес не найден или нет прав для выполнения команды',
            4: 'неверный размер пакета или не удалось сопоставить адрес с именем узла',
            5: 'тайм-аут запроса',
            6: 'запрос отменен или отправитель запретил фрагментацию, а пакет требует её фрагментации',
            7: 'защитный экран блокирует запрос или пакет отклонен',
            8: 'недостаточно памяти для выполнения запроса или маршрут к узлу недоступен',
            9: 'неверный параметр или сетевой администратор запретил ping по этому адресу',
            10: 'оборудование, не поддерживающее интерфейс IPv6, используется, чтобы подключиться к компьютеру, который работает с IPv6'
            }

        self.dict_out_code_server = {
            100: 'Continue',
            101: 'Switching Protocols', 102: 'Processing',
            200: 'OK', 201: 'Created', 202: 'Accepted',
            203: 'Non-Authoritative Information',
            204: 'No Content', 205: 'Reset Content',
            206: 'Partial Content', 207: 'Multi-Status',
            208: 'Already Reported', 226: 'IM Used',
            300: 'Multiple Choices', 301: 'Moved Permanently',
            302: 'Found', 303: 'See Other', 304: 'Not Modified',
            305: 'Use Proxy', 307: 'Temporary Redirect',
            308: 'Permanent Redirect',
            400: 'Bad Request', 401: 'Unauthorized', 402: 'Payment Required',
            403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed',
            406: 'Not Acceptable', 407: 'Proxy Authentication Required',
            408: 'Request Timeout', 409: 'Conflict', 410: 'Gone',
            411: 'Length Required', 412: 'Precondition Failed',
            413: 'Request Entity Too Large', 414: 'Request-URI Too Long',
            415: 'Unsupported Media Type', 416: 'Requested Range Not Satisfiable',
            417: 'Expectation Failed', 421: 'Misdirected Request',
            422: 'Unprocessable Entity', 423: 'Locked', 424: 'Failed Dependency',
            426: 'Upgrade Required', 428: 'Precondition Required', 429: 'Too Many Requests',
            431: 'Request Header Fields Too Large', 451: 'Unavailable For Legal Reasons',
            500: 'Internal Server Error', 501: 'Not Implemented', 502: 'Bad Gateway',
            503: 'Service Unavailable', 504: 'Gateway Timeout',
            505: 'HTTP Version Not Supported', 506: 'Variant Also Negotiates', 507: 'Insufficient Storage',
            508: 'Loop Detected', 510: 'Not Extended', 511: 'Network Authentication Required'
            }

    def get_is_working_server(self, host, type_host):
        # Получить код состояния сервера

        try:
            if type_host == 'url':
                response = requests.get(host, timeout=1)
                return self.dict_out_code_server[response.status_code]
            elif type_host == 'domaine':
                response = requests.get(f'http://{host}', timeout=1)
                return self.dict_out_code_server[response.status_code]
        except:
            return None

    def get_server_overload(self, host, type_host):
        # Проверка перегруженности сервера

        try:
            TIMEOUT_THRESHOLD = 4  # Пороговое значение времени ответа
            if type_host == 'url':
                response = requests.get(host, timeout=1)
            elif type_host == 'domaine':
                response = requests.get(f'http://{host}', timeout=1)
            response_time = response.elapsed.total_seconds()

            if response_time > TIMEOUT_THRESHOLD:
                return False
            else:
                return True
        except:
            return 'Ошибка'

    def ping(self, host):  # Проверка домена на доступность через ping

        # Параметр для количества пакетов в зависимости от ключей
        param = '-n' if platform.system().lower() == 'windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', host]

        # есть связь с сервером - 0, иначе - 1 или 2
        try:
            code = subprocess.call(command, timeout=1)
            return self.dict_out_code_ping[code]

        except subprocess.TimeoutExpired:
            return 'Ошибка при пинге'

    def is_port_open(self, ips, ports):  # Проверка порта
        # Проверяет, открыт ли порт с заданным номером на указанном IP-адресе,
        # переданных в функцию
        lst_ip_port_res = []

        if isinstance(ips, str):
            ips = [ips]

        for ip in ips:
            for port in ports:
                start = time.time()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    try:
                        s.connect((ip, port))

                        end = time.time()
                        rtt = (end - start) * 1000

                        lst_ip_port_res.append((ip, port,
                                                True, f'{rtt:.2f} ms'))
                    except:
                        end = time.time()
                        rtt = (end - start) * 1000
                        lst_ip_port_res.append((ip, port,
                                                False, f'{rtt:.2f} ms'))
        return lst_ip_port_res


class CheckServerAdapter:
    def __init__(self, host, type_host, ports):
        self.host = host
        self.type_host = type_host
        self.ports = ports
        self.module = CheckServer()

    def get_is_working_server(self):
        # Получить код состояния сервера
        return self.module.get_is_working_server(self.host, self.type_host)

    def get_server_overload(self):
        # Проверка перегруженности сервера
        return self.module.get_server_overload(self.host, self.type_host)

    def ping(self):  # Проверка домена на доступность через ping
        return self.module.ping(self.host)

    def is_port_open(self):  # Проверка порта
        return self.module.is_port_open(self.host, self.ports)

    def get_host(self):
        return self.host

    def get_type_host(self):
        return self.type_host
