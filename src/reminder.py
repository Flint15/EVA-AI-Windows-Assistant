import win32com.client
import datetime
import pythoncom
import config
def create_reminder(user_input:str):
    pythoncom.CoInitialize()
    try:
        info_reminder:list = [i.strip() for i in user_input.split('|')]
        
        if len(info_reminder) != 6:
            print('You have not entered enough or too many parameters to create a note!')
            return

        try:
            start_time = datetime.datetime.strptime(info_reminder[2], "%d.%m.%Y %H:%M")
        except ValueError:
            print('The format is entered incorrectly!')
            return

        try:
            outlook = win32com.client.gencache.EnsureDispatch('Outlook.Application')
            appointment = outlook.CreateItem(1)
            appointment.Subject = info_reminder[0]
            appointment.Body = info_reminder[1]
            appointment.Start = start_time.strftime('%d/%m/%Y %H:%M')
            appointment.Duration = int(info_reminder[3])
            appointment.Location = info_reminder[4]
            appointment.ReminderSet = True
            appointment.ReminderMinutesBeforeStart = int(info_reminder[5])
            appointment.BusyStatus = 2

            appointment.Save()
            appointment.Display()
            print('The event has been added!')

        except Exception as e:
            print(f'Error when creating an event: {e}')
    except Exception as e:
        print(f'Error when creating an event: {e}')
    finally:
        pythoncom.CoUninitialize()
    config.reminder_flag = False
if __name__ == '__main__':
    user_input = input('Message: ')
    print(create_reminder(user_input))