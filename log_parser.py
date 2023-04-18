import os
import re



class LogParser:
    def __init__(self, folder) -> None:
        self.folder = folder
        self.victims = []
        self.url_regex = re.compile("[a-zA-Z]+:\\/\\/(?:[^/\s]+@)?([^/\s]+)")
        self.file_names=["password", "Password", "passwords", "Passwords"]
        self.ext="txt"

    def parse_pwd_file(self,file_path):
        domain=""
        user=""
        passw=""
        count=0
        with open(file_path, encoding='latin-1') as f:
            lines = f.readlines()
            i=0
            while(i<len(lines)-2):
                if lines[i].find(":") != -1 and lines[i+1].find(":") != -1 and lines[i+2].find(":") != -1:
                    data=lines[i].split(":", 1)
                    x=data[1].strip()
                    match = self.url_regex.search(x)
                    if match:
                        domain=match.group(1)
                    else:
                        i+=1
                        continue
                    data=lines[i+1].split(":", 1)
                    x=data[1].strip()
                    user=x
                    data=lines[i+2].split(":", 1)
                    x=data[1].strip()
                    passw=x
                    if domain.isascii() and user.isascii() and passw.isascii():
                        self.victims.append({"url":domain,"username":user,"password":passw})
                        count+=1
                    i+=3
                else:
                    i+=1
        return count

    def parse_dir(self, dir):
        pwd_file=""
        for file in self.file_names:
            path=os.path.join(dir, f'{file}.{self.ext}')
            if os.path.isfile(path):
                print(f'[*] {path} exists!')
                pwd_file=path
                self.parse_pwd_file(pwd_file)
                break

        if pwd_file=="":
            for entry in os.scandir(dir):
                if entry.is_dir():
                    self.parse_dir(entry.path)
            print(f"[*] No passwords file in {dir}")

    def dict_to_tuple(self, d):
        # convert a dictionary to a tuple of sorted key-value pairs
        return tuple(sorted(d.items()))
    def parse_all(self):
        for entry in os.scandir(self.folder):
            if entry.is_dir():
                self.parse_dir(entry.path)
        self.parse_dir(self.folder)
        my_list = list(set(self.dict_to_tuple(d) for d in self.victims))

        # convert the tuples back to dictionaries
        self.victims = [dict(t) for t in my_list]
        return self.victims