import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import config


def send_mail_with_attachment(
        user_input: str
):
    """
    Отправляет письмо через Mail.ru с возможностью прикрепления файлов

    :param sender_email: Ваш email Mail.ru (например, example@mail.ru)
    :param sender_password: Пароль (или пароль приложения для 2FA)
    :param recipient_email: Email получателя
    :param subject: Тема письма
    :param body: Текст письма
    :param attachment_paths: Список путей к файлам для прикрепления (опционально)
    :param smtp_server: SMTP сервер (по умолчанию smtp.mail.ru)
    :param smtp_port: Порт SMTP (по умолчанию 465 для SSL)
    """

    mail_info: list = [i.strip() for i in user_input.split('|')]
    # Создаем сообщение
    msg = MIMEMultipart()
    msg['From'] = mail_info[0]
    msg['To'] = mail_info[2]
    msg['Subject'] = mail_info[3]

    if 'mail.ru' in mail_info[0]:
        smtp_server="smtp.mail.ru"
    elif 'gmail.com' in mail_info[0]:
        smtp_server = "smtp.gmail.com"
    elif 'yandex.ru' in mail_info[0]:
        smtp_server = "smtp.yandex.ru"
    else:
        return "Error - bad email address"
    smtp_port=465


    # Добавляем текст письма
    msg.attach(MIMEText(mail_info[4], 'plain'))

    # Добавляем вложения, если они есть
    if mail_info[5] != 'No':
        for attachment_path in mail_info[5]:
            try:
                # Проверяем существование файла
                if not os.path.isfile(attachment_path):
                    print(f"Файл не найден: {attachment_path}")
                    continue

                # Получаем имя файла
                filename = os.path.basename(attachment_path)

                # Открываем файл в бинарном режиме
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())

                # Кодируем файл в base64
                encoders.encode_base64(part)

                # Добавляем заголовки
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )

                # Прикрепляем файл к сообщению
                msg.attach(part)
                print(f"File added: {filename}")

            except Exception as e:
                return(f"Error because of adding a file {attachment_path}: {e}")

    try:
        # Отправляем письмо через SMTP с SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(mail_info[0], mail_info[1])
            server.sendmail(mail_info[0], mail_info[2], msg.as_string())
        config.mail_flag = False
        print("Письмо успешно отправлено!")

    except Exception as e:
        return(f"Ошибка при отправке письма: {e}")



