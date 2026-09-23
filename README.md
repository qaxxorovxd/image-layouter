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
   Shu yerda "Rasm to'liq tushsin (blur fon)" belgisini ham qo'yish mumkin; keyinchalik
   uni `B` klavishi bilan istalgan paytda yoqib-o'chirasiz.
4. Har bir rasm uchun kerakli qismni tanlang:

   | Klaviatura / sichqoncha         | Vazifasi                                        |
   |----------------------------------|--------------------------------------------------|
   | `W` `A` `S` `D` yoki strelkalar  | kesish ramkasini surish                          |
   | Sichqonchani bosib sudrash       | kesish ramkasini surish                          |
   | `1`                              | yaqinlashtirish (zoom in)                        |
   | `2`                              | uzoqlashtirish (zoom out)                        |
   | Sichqoncha g'ildiragi            | yaqinlashtirish / uzoqlashtirish                 |
   | `B`                              | rasm to'liq tushsin — bo'sh joy blur fon bilan   |
   | `P`                              | qog'ozni tik qo'yish (portret)                   |
   | `L`                              | qog'ozni yotqizish (landshaft)                   |
   | `N` yoki `Delete`                | rasmni o'tkazib yuborish (skip)                  |
   | `R`                              | joriy rasm sozlamalarini tiklash                 |
   | `K`                              | klavishlar ro'yxatini ochish/yopish              |
   | `Enter`, `Space` yoki `Esc`      | saqlash va keyingi rasmga o'tish                 |

   ### Ikki rejim: kesish va "to'liq + blur fon"

   Odatda rasm qog'oz nisbatiga moslab **kesiladi** — ya'ni chetlari tushib qoladi.
   Agar rasm to'liq tushishini xohlasangiz, `B` ni bosing: rasm butunligicha
   qog'ozga sig'diriladi, qog'ozning bo'sh (oq) qismi esa xuddi shu rasmning
   kattalashtirilgan va **blur qilingan** nusxasi bilan to'ldiriladi. Masalan 1:1
   rasm 10x15 sm qog'ozda — rasm o'rtada to'liq turadi, tepa va past qismi blur fon.

   `B` rejimida oyna to'g'ridan-to'g'ri **tayyor qog'ozni** ko'rsatadi, ya'ni
   printerdan nima chiqsa, o'shani. Bu rejimda surish/zoom kerak emas (rasm allaqachon
   to'liq). Yana `B` bosilsa, kesish rejimiga qaytadi. Rejim keyingi rasmlarda ham
   saqlanib qoladi. Blur kuchi, fon yorqinligi kabi sozlamalar `code/config.py` da
   (`BLUR_RADIUS_FRACTION`, `BLUR_BG_BRIGHTNESS`, `BLUR_BG_ZOOM`, `BLUR_FG_MARGIN`).

   ### O'tkazib yuborish (skip)

   Rasm yaroqsiz bo'lsa yoki hozir kerak bo'lmasa, `N` (yoki `Delete`) bosing:
   rasm chop etilmaydi, o'rniga `skipped-images/` papkasiga qo'yiladi va dastur
   keyingi rasmga o'tadi. Asl fayl `images/` da joyida qoladi (nusxa olinadi).
   Agar o'tkazilgan rasm `images/` dan **ko'chib ketsin** desangiz,
   `code/config.py` dagi `SKIP_MOVE_ORIGINAL` ni `True` qiling.

   O'tkazilgan rasmlar raqam olmaydi: 2-rasmni skip qilsangiz ham chiqish fayllari
   `1.png, 2.png, 3.png ...` bo'lib ketma-ket boraveradi, bo'shliq qolmaydi.
   Yuqoridagi qatorda nechta saqlangani va nechtasi o'tkazilgani yozilib turadi.

   ### Qog'oz holati: tik yoki yotiq

   `P` — qog'oz tik turadi (10x15), `L` — qog'oz yotqiziladi (15x10). Bu ikkalasi
   ish vaqtida istalgan paytda almashtiriladi va keyingi rasmlarga ham o'tadi;
   kesish ramkasi yangi nisbatga o'zi moslashadi. Boshlang'ich holat dialogda
   kiritilgan kenglik/balandlikdan olinadi (kenglik kattaroq bo'lsa — yotiq).

5. Oxirgi rasmni tasdiqlagach, saqlangan barcha rasmlar avtomatik ravishda
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
│   ├── render.py          # sahifani yig'ish: kesish yoki blur fon bilan to'liq sig'dirish
│   ├── config.py          # standart sozlamalar (DPI, zoom qadami, blur kuchi va h.k.)
│   └── utils.py            # fayllarni topish/tartiblash yordamchilari
├── images/                # BU YERGA rasmlaringizni soling
├── finished-images/       # natija shu yerga chiqadi
└── skipped-images/        # "N" bilan o'tkazib yuborilgan rasmlar
```

## Eslatmalar

- Rasmlar fayl nomi bo'yicha raqamli tartibda (`2.jpg` < `10.jpg`) ochiladi.
- Telefon kameralaridagi EXIF aylanish avtomatik to'g'irlanadi.
- Chiqish oynasidan `X` orqali yopsangiz, hali saqlanmagan progress yo'qoladi —
  saqlangan rasmlar `finished-images/`da qoladi.
