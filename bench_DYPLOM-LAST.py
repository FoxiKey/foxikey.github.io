import platform
import subprocess
import psutil
import wmi
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import yara
import os
import tkinter as tk
from tkinter import ttk
from threading import Thread
import sys


class BenchmarkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Benchmark")
        self.geometry("1100x600")
        self.resizable(False, False)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.battery_tab = ttk.Frame(self.notebook)
        self.cpu_tab = ttk.Frame(self.notebook)
        self.memory_tab = ttk.Frame(self.notebook)
        self.storage_tab = ttk.Frame(self.notebook)
        self.scan_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.battery_tab, text="Battery")
        self.notebook.add(self.cpu_tab, text="CPU")
        self.notebook.add(self.memory_tab, text="Memory")
        self.notebook.add(self.storage_tab, text="Storage")
        self.notebook.add(self.scan_tab, text="Scan")

        self.create_battery_tab()
        self.create_cpu_tab()
        self.create_memory_tab()
        self.create_storage_tab()
        self.create_scan_tab()

        self.scanning = False

    def create_battery_tab(self):
        # Ваш код для создания вкладки Battery
        battery_frame = ttk.LabelFrame(self.battery_tab, text="Battery Information")
        battery_frame.pack(padx=20, pady=20)

        battery_info = self.get_battery_info()
        battery_percent = self.get_battery_percent()

        # Calculate battery mark
        battery_mark = self.calculate_battery_mark(battery_percent)

        # Display battery information and mark as text
        battery_info_label = ttk.Label(battery_frame, text=battery_info)
        battery_info_label.pack()
        battery_mark_label = ttk.Label(battery_frame, text=f"Battery Mark: {battery_mark}/100")
        battery_mark_label.pack()

        # Create a pie chart to visualize battery percentage
        plt.figure(figsize=(6, 4))
        labels = ["Battery", "Remaining"]
        sizes = [battery_percent, 100 - battery_percent]
        colors = ["lightblue", "lightgray"]
        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        plt.axis("equal")
        plt.title("Battery Percentage")
        plt.savefig("battery_chart.png")

        # Display the battery chart image
        battery_chart_image = tk.PhotoImage(file="battery_chart.png")
        battery_chart_label = ttk.Label(battery_frame, image=battery_chart_image)
        battery_chart_label.image = battery_chart_image
        battery_chart_label.pack()

    def create_cpu_tab(self):
        # Ваш код для создания вкладки CPU
        cpu_frame = ttk.LabelFrame(self.cpu_tab, text="CPU Performance")
        cpu_frame.pack(padx=20, pady=20)

        cpu_info = self.get_cpu_info()

        # Calculate CPU mark
        cpu_mark = self.calculate_cpu_mark()

        # Display CPU information and mark as text
        cpu_info_label = ttk.Label(cpu_frame, text=cpu_info)
        cpu_info_label.pack()
        cpu_mark_label = ttk.Label(cpu_frame, text=f"CPU Mark: {cpu_mark}/100")
        cpu_mark_label.pack()

        # Create a bar chart to visualize CPU usage
        cpu_percentages = psutil.cpu_percent(interval=1, percpu=True)
        cores = [f"CPU{i + 1}" for i in range(len(cpu_percentages))]
        plt.figure(figsize=(11, 4))

        plt.bar(cores, cpu_percentages, color="#ffcc5f")
        plt.ylim(0, 100)
        plt.xlabel("CPU")
        plt.ylabel("Percentage")
        plt.title("CPU Usage")
        plt.gca().spines["right"].set_visible(False)
        plt.gca().spines["top"].set_visible(False)
        plt.gca().yaxis.set_ticks_position("left")
        plt.gca().xaxis.set_ticks_position("bottom")
        plt.grid(axis="y", linestyle="--", linewidth=0.7)
        plt.savefig("cpu_chart.png")

        # Display the CPU chart image
        cpu_chart_image = tk.PhotoImage(file="cpu_chart.png")
        cpu_chart_label = ttk.Label(cpu_frame, image=cpu_chart_image)
        cpu_chart_label.image = cpu_chart_image
        cpu_chart_label.pack()

    def create_memory_tab(self):
        # Ваш код для создания вкладки Memory
        memory_frame = ttk.LabelFrame(self.memory_tab, text="Memory Usage")
        memory_frame.pack(padx=20, pady=20)

        memory_info = self.get_memory_info()

        # Calculate memory mark
        memory_mark = self.calculate_memory_mark()

        # Display memory information and mark as text
        memory_info_label = ttk.Label(memory_frame, text=memory_info)
        memory_info_label.pack()
        memory_mark_label = ttk.Label(memory_frame, text=f"Memory Mark: {memory_mark}/100")
        memory_mark_label.pack()

        # Create a pie chart to visualize memory usage
        memory_usage = psutil.virtual_memory()
        plt.figure(figsize=(6, 4))
        labels = ["Used", "Available"]
        sizes = [memory_usage.used, memory_usage.available]
        colors = ["#ffcc5f", "lightgray"]
        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        plt.axis("equal")
        plt.title("Memory Usage")
        plt.savefig("memory_chart.png")

        # Display the memory chart image
        memory_chart_image = tk.PhotoImage(file="memory_chart.png")
        memory_chart_label = ttk.Label(memory_frame, image=memory_chart_image)
        memory_chart_label.image = memory_chart_image
        memory_chart_label.pack()

    def create_storage_tab(self):
        # Ваш код для создания вкладки Storage
        storage_frame = ttk.LabelFrame(self.storage_tab, text="Storage Performance")
        storage_frame.pack(padx=20, pady=20)

        storage_info = self.get_storage_info()

        # Calculate SSD speed mark
        ssd_speed = self.get_ssd_speed()
        ssd_mark = self.calculate_ssd_mark(ssd_speed)

        # Display storage information and SSD mark as text
        storage_info_label = ttk.Label(storage_frame, text=storage_info)
        storage_info_label.pack()
        ssd_mark_label = ttk.Label(storage_frame, text=f"SSD Speed Mark: {ssd_mark}/100")
        ssd_mark_label.pack()

        # Create a bar chart to visualize total and used sizes of storage
        partitions = psutil.disk_partitions()
        total_sizes = []
        used_sizes = []
        for partition in partitions:
            if platform.system() == "Windows":
                if "cdrom" in partition.opts or partition.fstype == "":
                    continue
            elif platform.system() == "Darwin":
                if "/Volumes" in partition.mountpoint:
                    continue
            else:
                if "/media" in partition.mountpoint:
                    continue

            usage = psutil.disk_usage(partition.mountpoint)
            total_sizes.append(usage.total)
            used_sizes.append(usage.used)

        plt.figure(figsize=(6, 4))
        plt.bar(range(len(total_sizes)), total_sizes, color="#ffcc5f", label="Total Size")
        plt.bar(range(len(used_sizes)), used_sizes, color="#ff3d3d", label="Used Size")
        plt.xticks(range(len(partitions)), [partition.device for partition in partitions], rotation=45)
        plt.xlabel("Storage")
        plt.ylabel("Size (bytes)")
        plt.title("Storage Usage")
        plt.legend()
        plt.gca().spines["right"].set_visible(False)
        plt.gca().spines["top"].set_visible(False)
        plt.gca().yaxis.set_ticks_position("left")
        plt.gca().xaxis.set_ticks_position("bottom")
        plt.grid(axis="y", linestyle="--", linewidth=0.5)
        plt.tight_layout()
        plt.savefig("storage_chart.png")

        # Display the storage chart image
        storage_chart_image = tk.PhotoImage(file="storage_chart.png")
        storage_chart_label = ttk.Label(storage_frame, image=storage_chart_image)
        storage_chart_label.image = storage_chart_image
        storage_chart_label.pack()

        ######TEST
    def get_battery_info(self):
            battery = psutil.sensors_battery()
            if battery.power_plugged:
                status = "Plugged in"
            else:
                status = "Not plugged in"
            info = f"Status: {status}\nPercentage: {battery.percent}%"
            return info

    def get_battery_percent(self):
            battery = psutil.sensors_battery()
            return battery.percent

    def calculate_battery_mark(self, battery_percent):
            if battery_percent < 75:
                return 15
            else:
                return 30

    def get_cpu_info(self):
            cpu_info = f"Processor: {platform.processor()}\n"
            cpu_info += f"Physical Cores: {psutil.cpu_count(logical=False)}\n"
            cpu_info += f"Total Cores: {psutil.cpu_count(logical=True)}"
            return cpu_info

    def calculate_cpu_mark(self):
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_mark = 100 - cpu_percent
            return cpu_mark

    def get_memory_info(self):
            memory_usage = psutil.virtual_memory()
            total_size = self.format_size(memory_usage.total)
            used_size = self.format_size(memory_usage.used)
            memory_info = f"Total: {total_size}\nUsed: {used_size}"
            return memory_info

    def calculate_memory_mark(self):
            memory_usage = psutil.virtual_memory()
            memory_mark = (memory_usage.available / memory_usage.total) * 100
            return memory_mark

    def get_storage_info(self):
            partitions = psutil.disk_partitions()
            storage_info = ""
            for partition in partitions:
                if platform.system() == "Windows":
                    if "cdrom" in partition.opts or partition.fstype == "":
                        continue
                elif platform.system() == "Darwin":
                    if "/Volumes" in partition.mountpoint:
                        continue
                else:
                    if "/media" in partition.mountpoint:
                        continue

                usage = psutil.disk_usage(partition.mountpoint)
                total_size = self.format_size(usage.total)
                used_size = self.format_size(usage.used)

                storage_info += f"Total Size: {total_size}\n"
                storage_info += f"Used Size: {used_size}\n"

            return storage_info

    def get_ssd_speed(self):
            c = wmi.WMI()
            ssd_speed = {}
            for disk in c.Win32_DiskDrive(MediaType='SSD'):
                drive = disk.Name
                interface_type = disk.InterfaceType
                cmd = f"wmic diskdrive where Name='{drive}' get BytesPerSector /format:list"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                lines = output.split('\n')
                for line in lines:
                    if line.startswith('BytesPerSector='):
                        bytes_per_sector = int(line.split('=')[1])
                        break
                else:
                    bytes_per_sector = None
                if bytes_per_sector is not None and interface_type == 'Solid State':
                    cmd = f"winsat disk -drive {drive}"
                    speed_output = subprocess.check_output(cmd, shell=True).decode().strip()
                    speed_lines = speed_output.split('\n')
                    for speed_line in speed_lines:
                        if speed_line.startswith('Disk Sequential'):
                            speed = speed_line.split(': ')[1].strip().split()[0]
                            ssd_speed[drive] = int(speed)
            return ssd_speed

    def calculate_ssd_mark(self, ssd_speed):
            ssd_mark = 100
            for drive, speed in ssd_speed.items():
                if speed < 200:
                    ssd_mark -= 10
            return ssd_mark

        ####test

    def create_scan_tab(self):
        scan_frame = ttk.LabelFrame(self.scan_tab, text="Scan for Malware")
        scan_frame.pack(padx=20, pady=20)

        self.scan_option = tk.StringVar()
        self.scan_option.set("1")

        ttk.Radiobutton(scan_frame, text="Сканировать определенный диск", variable=self.scan_option, value="1").pack(
            anchor=tk.W)
        ttk.Radiobutton(scan_frame, text="Полное сканирование всех дисков", variable=self.scan_option, value="2").pack(
            anchor=tk.W)

        self.disk_entry = ttk.Entry(scan_frame)
        self.disk_entry.pack()

        self.scan_button = ttk.Button(scan_frame, text="Начать сканирование", command=self.start_scan)
        self.scan_button.pack()

        self.stop_button = ttk.Button(scan_frame, text="Остановить сканирование", command=self.stop_scan)
        self.stop_button.pack()

        self.progress_label = ttk.Label(scan_frame, text="Прогресс: 0%")
        self.progress_label.pack()

        self.result_text = tk.Text(scan_frame, height=10, width=80)
        self.result_text.pack()

    def start_scan(self):
        self.result_text.delete(1.0, tk.END)
        self.progress_label.config(text="Прогресс: 0%")
        scan_option = self.scan_option.get()
        disk = self.disk_entry.get().upper()
        self.scanning = True

        if scan_option == "1" and disk:
            scan_path = f"{disk}:/"
            if not os.path.exists(scan_path):
                self.result_text.insert(tk.END, f"Путь {scan_path} не существует.\n")
                return
            thread = Thread(target=self.scan_for_malware, args=(scan_path,))
            thread.start()
        elif scan_option == "2":
            thread = Thread(target=self.scan_all_disks)
            thread.start()
        else:
            self.result_text.insert(tk.END, "Неверный выбор.\n")

    def stop_scan(self):
        self.scanning = False
        self.result_text.insert(tk.END, "Сканирование остановлено пользователем.\n")

    def scan_directory(self, directory, rules):
        matches = []
        total_files = sum([len(files) for r, d, files in os.walk(directory)])
        scanned_files = 0

        with open("scan_errors.txt", "w") as error_file:
            for root, dirs, files in os.walk(directory):
                if not self.scanning:
                    break
                for file in files:
                    if not self.scanning:
                        break
                    file_path = os.path.join(root, file)
                    try:
                        match = rules.match(file_path)
                        if match:
                            matches.append((file_path, match))
                    except Exception as e:
                        error_file.write(f"Ошибка при сканировании файла {file_path}: {e}\n")

                    scanned_files += 1
                    progress = (scanned_files / total_files) * 100
                    self.progress_label.config(text=f"Прогресс: {progress:.2f}%")
                    self.update_idletasks()

        self.progress_label.config(text="Сканирование завершено.")
        return matches

    # Рекурсивная функция для сбора всех .yara файлов в директориях
    def collect_yara_files(self, directory):
        yara_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.yara') or file.endswith('.yar'):
                    yara_files.append(os.path.join(root, file))
        return yara_files

    def scan_for_malware(self, scan_path):
        # Путь к папке с .yara файлами
        rules_path = r'C:/Users/foxik/OneDrive/Рабочий стол/ДИПЛОМ_МАГІСТР/malware-yara-main'

        # Проверяем, существует ли путь для сканирования
        if not os.path.exists(scan_path):
            self.result_text.insert(tk.END, f"Путь {scan_path} не существует.\n")
            return []

        # Собираем все файлы .yara из папки и подпапок
        rules_files = self.collect_yara_files(rules_path)

        if not rules_files:
            self.result_text.insert(tk.END, "Нет файлов .yara для компиляции.\n")
            return []

        # Компилируем все правила из файлов
        try:
            rules = yara.compile(filepaths={f'rule_{i}': rules_files[i] for i in range(len(rules_files))})
        except yara.YaraSyntaxError as e:
            self.result_text.insert(tk.END, f"Ошибка компиляции правил Yara: {e}\n")
            return []

        # Выполняем сканирование директории
        matches = self.scan_directory(scan_path, rules)
        self.display_results(matches)

    # Функция для сканирования всех дисков
    def scan_all_disks(self):
        # Путь к папке с .yara файлами
        rules_path = r'C:/Users/foxik/OneDrive/Рабочий стол/ДИПЛОМ_МАГІСТР/malware-yara-main'

        # Собираем все файлы .yara из папки и подпапок
        rules_files = self.collect_yara_files(rules_path)

        if not rules_files:
            self.result_text.insert(tk.END, "Нет файлов .yara для компиляции.\n")
            return []

        # Компилируем все правила
        try:
            rules = yara.compile(filepaths={f'rule_{i}': rules_files[i] for i in range(len(rules_files))})
        except yara.Error as e:
            self.result_text.insert(tk.END, f"Ошибка компиляции правил Yara: {e}\n")
            return []

        malware_matches = []

        # Сканируем все диски
        for disk in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if not self.scanning:
                break
            scan_path = f"{disk}:/"
            if os.path.exists(scan_path):
                matches = self.scan_directory(scan_path, rules)
                malware_matches.extend(matches)

        self.display_results(malware_matches)

    def display_results(self, matches):
        if matches:
            self.result_text.insert(tk.END, "Вредоносное ПО обнаружено!\n")
            for match in matches:
                short_path = os.path.basename(match[0])
                self.result_text.insert(tk.END, f"Файл: {short_path}, Совпадения: {match[1]}\n")
        else:
            self.result_text.insert(tk.END, "Вредоносное ПО не обнаружено.\n")

    @staticmethod
    def format_size(size):
        power = 2 ** 10
        n = 0
        power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels[n]}B"
if __name__ == "__main__":
    app = BenchmarkApp()
    app.mainloop()
