import cv2
import wx
import threading
import numpy as np


class CameraViewer(wx.Frame):
    def __init__(self, parent, title):
        super(CameraViewer, self).__init__(parent, title=title, size=(800, 800))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(50, 50, 50))  # Set background color to gray

        self.SetForegroundColour(wx.Colour(255, 255, 255))  # Set text color to white

        self.ip_label = wx.StaticText(self.panel, label="Camera IP:")
        self.ip_label.SetForegroundColour(wx.Colour(255, 255, 255))  # Set label text color to white
        self.ip_entry = wx.TextCtrl(self.panel)
        self.port_label = wx.StaticText(self.panel, label="Camera Port:")
        self.port_label.SetForegroundColour(wx.Colour(255, 255, 255))  # Set label text color to white
        self.port_entry = wx.TextCtrl(self.panel)
        self.url_label = wx.StaticText(self.panel, label="Camera URL:")
        self.url_label.SetForegroundColour(wx.Colour(255, 255, 255))  # Set label text color to white
        self.url_entry = wx.TextCtrl(self.panel)
        self.protocol_label = wx.StaticText(self.panel, label="Protocol:")
        self.protocol_label.SetForegroundColour(wx.Colour(255, 255, 255))  # Set label text color to white
        self.protocol_choice = wx.Choice(self.panel, choices=["rtsp", "http", "udp", "tcp"])
        self.protocol_choice.SetSelection(0)
        self.image_type_label = wx.StaticText(self.panel, label="Image Type:")
        self.image_type_label.SetForegroundColour(wx.Colour(255, 255, 255))  # Set label text color to white
        self.image_type_choice = wx.Choice(self.panel, choices=["png", "jpg", "jpeg", "bmp"])
        self.image_type_choice.SetSelection(0)
        self.color_type_label = wx.StaticText(self.panel, label="Color Type:")
        self.color_type_label.SetForegroundColour(wx.Colour(255, 255, 255))  # Set label text color to white
        self.color_type_choice = wx.Choice(self.panel, choices=["RGB", "BGR", "GRAY"])
        self.color_type_choice.SetSelection(0)
        self.connection_type_label = wx.StaticText(self.panel, label="Connection Type:")
        self.connection_type_label.SetForegroundColour(wx.Colour(255, 255, 255))  # Set label text color to white
        self.connection_type_choice = wx.Choice(self.panel,
                                                choices=["CAP_FFMPEG", "CAP_GSTREAMER", "CAP_V4L2"])
        self.connection_type_choice.SetSelection(0)

        self.connect_button = wx.Button(self.panel, label="Connect")
        self.connect_button.SetBackgroundColour(wx.Colour(30, 30, 30))  # Set button color to dark gray
        self.connect_button.SetForegroundColour(wx.Colour(255, 255, 255))  # Set button text color to white
        self.connect_button.Bind(wx.EVT_BUTTON, self.connect)

        self.canvas = wx.StaticBitmap(self.panel, size=(640, 360))

        self.bmp = wx.Bitmap(640, 480)  # Create and initialize the wx.Bitmap

        self.capture = None
        self.thread = None
        self.is_running = False

        self.title = wx.StaticText(self.panel, label="Camera Viewer")
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title.SetFont(font)
        self.title.SetForegroundColour(wx.Colour(255, 255, 255))  # Set title text color to white

        self.layout_ui()

    def layout_ui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title, flag=wx.CENTER | wx.TOP, border=10)

        grid = wx.GridSizer(7, 2, 5, 5)
        grid.Add(self.ip_label, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        grid.Add(self.ip_entry, flag=wx.ALL | wx.EXPAND, border=5)
        grid.Add(self.port_label, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        grid.Add(self.port_entry, flag=wx.ALL | wx.EXPAND, border=5)
        grid.Add(self.url_label, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        grid.Add(self.url_entry, flag=wx.ALL | wx.EXPAND, border=5)
        grid.Add(self.protocol_label, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        grid.Add(self.protocol_choice, flag=wx.ALL | wx.EXPAND, border=5)
        grid.Add(self.image_type_label, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        grid.Add(self.image_type_choice, flag=wx.ALL | wx.EXPAND, border=5)
        grid.Add(self.color_type_label, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        grid.Add(self.color_type_choice, flag=wx.ALL | wx.EXPAND, border=5)
        grid.Add(self.connection_type_label, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        grid.Add(self.connection_type_choice, flag=wx.ALL | wx.EXPAND, border=5)

        vbox.Add(grid, flag=wx.ALL | wx.EXPAND, border=10)
        vbox.Add(self.connect_button, flag=wx.CENTER, border=10)
        vbox.Add(self.canvas, flag=wx.CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.panel.SetSizer(vbox)
        self.Centre()
        self.Show()

    def connect(self, event):
        if self.is_running:
            return

        ip = self.ip_entry.GetValue()
        port = self.port_entry.GetValue()
        url = self.url_entry.GetValue()
        protocol = self.protocol_choice.GetStringSelection()
        image_type = "." + self.image_type_choice.GetStringSelection()
        color_type = cv2.COLOR_BGR2RGB if self.color_type_choice.GetStringSelection() == "RGB" else cv2.COLOR_BGR2GRAY
        connection_type = getattr(cv2, self.connection_type_choice.GetStringSelection())

        if (ip and port) or url:
            if url:
                camera_url = url
            else:
                camera_url = f"{protocol}://{ip}:{port}"

            self.capture = cv2.VideoCapture(camera_url, connection_type)

            if not self.capture.isOpened():
                print("Failed to open camera stream.")
                return

            self.is_running = True
            self.thread = threading.Thread(target=self.update, args=(color_type, image_type))
            self.thread.start()

    def update(self, color_type, image_type):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, color_type)
            frame = cv2.resize(frame, (640, 480))

            self.bmp.CopyFromBuffer(frame)
            wx.CallAfter(self.canvas.SetBitmap, self.bmp)  # Update the wx.Bitmap

            try:
                _, frame_data = cv2.imencode(image_type, frame)
                if frame_data is not None:
                    wx_image = wx.Image(640, 480, frame_data.tobytes())
                    wx_bitmap = wx.Image.ConvertToBitmap(wx_image)
                    wx.CallAfter(self.ImgControl2.SetBitmap, wx_bitmap)
                else:
                    print("Invalid frame data")

            except Exception as e:
                print('Error processing frame:', str(e))
        else:
            self.is_running = False
            self.capture.release()
            wx.CallAfter(self.canvas.SetBitmap, None)  # Clear the wx.Bitmap

    def close(self, event):
        self.is_running = False
        if self.capture:
            self.capture.release()
        self.Destroy()


if __name__ == "__main__":
    app = wx.App()
    frame = CameraViewer(None, title="Camera Viewer")
    frame.Bind(wx.EVT_CLOSE, frame.close)
    app.MainLoop()
