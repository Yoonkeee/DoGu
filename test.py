from PyQt5.QtGui import *
import os

# 현재 폴더에 현재 날짜의 폴더 이름 만들기
folderName = os.getcwd() + '\\' + str(time.localtime().tm_year) + '_' + str(time.localtime().tm_mon) + '_' + str(
            time.localtime().tm_mday)

# 폴더 생성
try:
    if not (os.path.isdir(folder_name)):
        os.makedirs(os.path.join(folder_name))
except OSError as e:
    print(e)

# 폴더에 있는 파일 리스트를 불러옴
file_list = os.listdir(folder_name)

if len(file_list) > 0:
    png_list = []
    # 그림파일 확장자 명만 찾아서 리스트에 추가
    for file_name in file_list:
        if (file_name.find('.png') == len(file_name)-4) or (file_name.find('.jpg') == len(file_name)-4):
            png_list.append(file_name)

    # 그림파일을 하나씩 로드함
    if len(png_list) > 0:
        for png_file in png_list:
            pixmap = QPixmap(folder_name+'\\'+png_file)

            png_path = folder_name+'\\'+png_file
            PNG_LIST.append(png_path)

lbl_img = QLabel()
clickable(lbl_img).connect(self.pictureListClicked)

lbl_img.setAlignment(Qt.AlignCenter)
lbl_img.setPixmap(pixmap)

def clickable(widget):
global FILE_LIST
    class Filter(QObject):

        clicked = pyqtSignal()

        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        # The developer can opt for .emit(obj) to get the object within the slot.
                        return True

            return False

    filter = Filter(widget)
    widget.installEventFilter(filter)
    FILE_LIST.append(filter)
    return filter.clicked