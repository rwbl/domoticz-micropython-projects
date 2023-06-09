"""
ssd1306ex.py
20230324
MicroPython SSD1306 OLED driver, I2C and SPI interfaces
Forked from https://github.com/stlehmann/micropython-ssd1306. Many thanks to the author.
There is also a MicroPython lib holding this library: https://github.com/micropython/micropython-lib.
Enhancements by rwbl
col and row definitions - for writing text, the col width is 8, row height is 16.
text_col_row(self, text, col, row) - Write text at row 0-3 and col 0-15.
text_block(self, block, title, value) - Write title & value in a text block. Max 6 text blocks.
text_rows(self, row1="", row2="", row3="", row4="") - Display text at col 0 on rows 1 to 4.
clear(self) - Clear the display.
Notes
A character has a size 8px width x 16px height. Max chars per row is 16, max rows is 4.
The starting index for the cols and rows is 0.
"""
# Imports
from micropython import const
import framebuf
# Register definitions
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)
# Default I2C address
I2C_ADDRESS = const(0x3C)
# Default pin numbers for SDA and SCL
PIN_SDA = const(0)	# GP0 (Pin #1 , I2C0 SDA)
PIN_SCL = const(1)	# GP1 (Pin #2 , I2C0 SCL)
# Display default pixel width and height
DISPLAY_WIDTH = const(128)
DISPLAY_HEIGHT = const(64)
# Text col and row definitions. Width & height in px
COL_WIDTH = const(8)
ROW_HEIGHT = const(16)
COL_MIN = const(0)
COL_MAX = const(15)
ROW_MIN = const(0)
ROW_MAX = const(3)
# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()
    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,  # off
            # address setting
            SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST,
            0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            # charge pump
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):  # on
            self.write_cmd(cmd)
        # Clear the display by filling 0
        self.fill(0)
        self.show()
    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)
    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)
    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)
    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))
    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)
        
    def text_col_row(self, text, col, row):
        """
        Write text at row 0-3 and col 0-15.
        """
        if not COL_MIN <= col <= COL_MAX:
            raise RuntimeError(f'Col index {col} out of range 0-15')
        if not ROW_MIN <= row <= ROW_MAX:
            raise RuntimeError(f'Row index {row} out of range 0-3')
        self.text(text, col * COL_WIDTH, row * ROW_HEIGHT)
    def text_block(self, block, title, value):
        """
        Set the title and value for a block.
        There are two rows: top for blocks 1-3 at rows 0,1 and bottom for blocks 4-6 at rows 2,3.
        The three block cols start at position 1, 6, 11.
        The first (position 0) and last (position 15) col are spaces.
        Between each block there is also a space (positions 5, 10).
        
        : param int block
            Block number 1-6. Blocks 1-3 are top row, 4-6 bottom row.
            
        :param string title
            Block title.
            
        :param int|string value
            The value to be display (as string) underneath the block title.
        """
        
        # Convert the value to a string
        value = str(value)
        # Check the text length. Max length of text in a block is 4.
        if len(title) > 4:
            title = title[0:4]
        if len(value) > 4:
            value = value[0:4]
        # Select each of the blocks and set the title & value
        if block == 1:
            self.text_col_row(title, 1, 0)
            self.text_col_row(value, 1, 1)
        elif block == 2:
            self.text_col_row(title, 6, 0)
            self.text_col_row(value, 6, 1)
        elif block == 3:
            self.text_col_row(title, 11, 0)
            self.text_col_row(value, 11, 1)
        elif block == 4:
            self.text_col_row(title, 1, 2)
            self.text_col_row(value, 1, 3)
        elif block == 5:
            self.text_col_row(title, 6, 2)
            self.text_col_row(value, 6, 3)
        elif block == 6:
            self.text_col_row(title, 11, 2)
            self.text_col_row(value, 11, 3)
        else:
            print(f'[ERROR] Block {block} out of range 1-6')
    def text_rows(self, row1="", row2="", row3="", row4=""):
        """
        Display text at col 0 on rows 1 to 4.
        """
        self.fill(0)
        self.text_col_row(row1, 0, 0)
        self.text_col_row(row2, 0, 1)
        self.text_col_row(row3, 0, 2)
        self.text_col_row(row4, 0, 3)
        self.show()
    def clear(self):
        """
        Clear the display.
        """
        self.fill(0)
        self.show()
class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        super().__init__(width, height, external_vcc)
    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)
    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)
class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        import time
        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        super().__init__(width, height, external_vcc)
    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)
    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)
