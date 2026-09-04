# Image Layouter

Ko'p sonli rasmlarni (masalan, 40 ta) belgilangan qog'oz o'lchamiga (masalan,
10x15 sm) qo'l bilan kesib/joylashtirib, ketma-ket raqamlangan holda
`finished-images/` papkasiga chiqaruvchi oddiy GUI dastur.

## O'rnatish

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt
```

> Linux'da ba'zi distributivlarda (masalan, Arch, Debian/Ubuntu) Tkinter
> alohida paket sifatida kerak bo'lishi mumkin:
> Arch: `sudo pacman -S tk` · Debian/Ubuntu: `sudo apt install python3-tk`
> Windows va macOS uchun rasmiy python.org o'rnatuvchisida Tkinter allaqachon bor.

## Ishlatish

1. Rasmlaringizni `images/` papkasiga soling (jpg, jpeg, png, bmp, webp, tif, gif).
2. Dasturni ishga tushiring:

   ```bash
   python run.py
   ```

3. Ochilgan oynada qog'oz o'lchamini (sm) va DPI ni kiriting — standart 10x15 sm, 300 DPI.
4. Har bir rasm uchun kerakli qismni tanlang:

   | Klaviatura / sichqoncha              | Vazifasi                          |
   |---------------------------------------|------------------------------------|
   | `W` `A` `S` `D` yoki strelkalar       | kesish ramkasini surish            |
   | Sichqonchani bosib sudrash            | kesish ramkasini surish            |
   | `1`                                    | yaqinlashtirish (zoom in)          |
   | `2`                                    | uzoqlashtirish (zoom out)          |
   | Sichqoncha g'ildiragi                  | yaqinlashtirish / uzoqlashtirish   |
   | `Enter`, `Space` yoki `Esc`           | saqlash va keyingi rasmga o'tish   |

5. Oxirgi rasmni tasdiqlagach, barcha kesilgan rasmlar avtomatik ravishda
   `finished-images/` papkasiga `1.png`, `2.png`, ... `N.png` nomlar bilan,
   tanlangan sm o'lchamiga mos piksel o'lchamda (masalan 10x15 sm @ 300 DPI
   → 1181x1772px) saqlanadi.

## Loyiha tuzilishi

```
image-layouter/
├── run.py               # ishga tushirish nuqtasi
├── requirements.txt
├── code/
│   ├── app.py            # GUI va asosiy mantiq
│   ├── config.py          # standart sozlamalar (DPI, zoom qadami va h.k.)
│   └── utils.py            # fayllarni topish/tartiblash yordamchilari
├── images/                # BU YERGA rasmlaringizni soling
└── finished-images/       # natija shu yerga chiqadi
```

## Eslatmalar

- Rasmlar fayl nomi bo'yicha raqamli tartibda (`2.jpg` < `10.jpg`) ochiladi.
- Telefon kameralaridagi EXIF aylanish avtomatik to'g'irlanadi.
- Chiqish oynasidan `X` orqali yopsangiz, hali saqlanmagan progress yo'qoladi —
  saqlangan rasmlar `finished-images/`da qoladi.
