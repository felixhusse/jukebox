try:
    import RPi.GPIO as GPIO
    from mfrc522 import MFRC522, SimpleMFRC522
except ImportError:
    from .mockups import MFRC522, GPIO, SimpleMFRC522

class HigherGainSimpleMFRC522(SimpleMFRC522):

    def __init__(self):
        self.READER = HigherGainMFRC522()

class HigherGainMFRC522(MFRC522):

    def MFRC522_Init(self):
        self.MFRC522_Reset()
        self.Write_MFRC522(self.TModeReg, 0x8D)
        self.Write_MFRC522(self.TPrescalerReg, 0x3E)
        self.Write_MFRC522(self.TReloadRegL, 30)
        self.Write_MFRC522(self.TReloadRegH, 0)

        self.Write_MFRC522(self.TxAutoReg, 0x40)
        self.Write_MFRC522(self.ModeReg, 0x3D)
        self.Write_MFRC522(self.RFCfgReg, 0x07 << 4)
        self.AntennaOn()