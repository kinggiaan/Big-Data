# Hướng dẫn cơ bản sử dụng LaTeX cho người mới bắt đầu

LaTeX (đọc là *Lay-tech* hoặc *Lah-tech*) là một hệ thống soạn thảo văn bản chất lượng cao, thường được sử dụng để viết các tài liệu khoa học, báo cáo kỹ thuật, luận văn, và các tài liệu có chứa nhiều công thức toán học.

Khác với Microsoft Word (bạn thấy gì thì in ra thế ấy - WYSIWYG), LaTeX hoạt động giống như lập trình: bạn viết "code" (nội dung + các thẻ định dạng), sau đó "biên dịch" (compile) để tạo ra file PDF hoàn chỉnh.

---

## 1. Cần chuẩn bị gì để dùng LaTeX?

Bạn có 2 cách để bắt đầu:

### Cách 1: Dùng Online (Khuyên dùng cho người mới)
Sử dụng trang web **Overleaf** (https://www.overleaf.com/).
- **Ưu điểm:** Không cần cài đặt gì cả, có sẵn mọi template, dễ dàng làm việc nhóm (như Google Docs).
- **Cách dùng:** Tạo tài khoản -> New Project -> Upload folder code LaTeX của bạn lên (ví dụ folder `Report_Midterm`) -> Bấm nút **Recompile** (màu xanh lá) để xem PDF.

### Cách 2: Cài đặt trên máy tính (Local)
Nếu bạn muốn dùng offline trên VSCode/Cursor:
1. Cài đặt **MiKTeX** (Windows) hoặc **MacTeX** (macOS). Đây là "bộ não" biên dịch LaTeX.
2. Cài extension **LaTeX Workshop** trong VSCode/Cursor.
3. Mở file `.tex` chính (ví dụ `BigData_Midterm_Group11.tex`), bấm nút Play/Build trên góc phải để tạo ra file PDF.

---

## 2. Cấu trúc của một file LaTeX

Một file LaTeX (`.tex`) luôn có 2 phần chính:

```latex
% --- PHẦN 1: PREAMBLE (Phần khai báo) ---
\documentclass[12pt]{report} % Khai báo loại tài liệu (article, report, book)
\usepackage[utf8]{inputenc}  % Khai báo các gói thư viện (packages) cần dùng
\usepackage{graphicx}        % Gói dùng để chèn hình ảnh

% --- PHẦN 2: DOCUMENT BODY (Nội dung chính) ---
\begin{document}

% Nội dung bài viết của bạn nằm ở đây

\end{document}
```
*Lưu ý: Ký tự `%` dùng để viết comment (ghi chú), LaTeX sẽ bỏ qua các dòng bắt đầu bằng `%`.*

---

## 3. Các lệnh cơ bản thường dùng

### 3.1. Chia bố cục bài viết
Tùy vào `\documentclass` mà bạn có các cấp độ chia mục khác nhau. Với `report` hoặc `book`, bạn có:

```latex
\chapter{Tên Chương}      % Chương 1
\section{Tên Mục}         % Mục 1.1
\subsection{Tên Tiểu mục} % Mục 1.1.1
```

### 3.2. Định dạng chữ
```latex
\textbf{Chữ in đậm}
\textit{Chữ in nghiêng}
\underline{Chữ gạch chân}
\texttt{Chữ dạng code (monospace)}
```

### 3.3. Tạo danh sách (List)
**Danh sách có đánh dấu chấm (Bullet points):**
```latex
\begin{itemize}
    \item Ý thứ nhất
    \item Ý thứ hai
    \begin{itemize} % Danh sách lồng nhau
        \item Ý nhỏ bên trong
    \end{itemize}
\end{itemize}
```

**Danh sách có đánh số (Numbered list):**
```latex
\begin{enumerate}
    \item Bước 1
    \item Bước 2
\end{enumerate}
```

### 3.4. Chèn hình ảnh
Để chèn hình, bạn cần gói `\usepackage{graphicx}` ở phần Preamble.

```latex
\begin{figure}[h!] % [h!] nghĩa là "đặt hình ở ngay vị trí này nếu có thể"
    \centering % Căn giữa hình
    \includegraphics[width=0.8\textwidth]{images/ten_hinh.png} % Đường dẫn tới hình
    \caption{Đây là chú thích của hình ảnh} % Chú thích bên dưới hình
    \label{fig:hinh1} % Nhãn để trích dẫn chéo
\end{figure}
```

### 3.5. Chèn bảng biểu (Table)
Tạo bảng trong LaTeX hơi phức tạp, bạn nên dùng trang web [TablesGenerator](https://www.tablesgenerator.com/) để vẽ bảng bằng giao diện trực quan, sau đó copy code LaTeX dán vào bài.

Cấu trúc cơ bản:
```latex
\begin{table}[h!]
    \centering
    \begin{tabular}{|c|l|r|} % 3 cột: căn giữa (c), căn trái (l), căn phải (r). Dấu | là kẻ viền dọc
        \hline % Kẻ đường viền ngang
        Cột 1 & Cột 2 & Cột 3 \\ \hline % Dấu & để ngăn cách cột, \\ để xuống dòng
        A & B & C \\ \hline
        X & Y & Z \\ \hline
    \end{tabular}
    \caption{Chú thích của bảng}
\end{table}
```

### 3.6. Viết công thức toán học
Đây là sức mạnh lớn nhất của LaTeX.
- **Công thức cùng dòng với chữ (Inline):** kẹp giữa 2 dấu `$`. Ví dụ: `$E = mc^2$` sẽ hiển thị $E = mc^2$.
- **Công thức đứng riêng một dòng (Display):**
```latex
\begin{equation}
    f(x) = \sum_{i=1}^{n} (x_i - \mu)^2
\end{equation}
```

---

## 4. Quản lý dự án lớn (Nhiều file)

Thay vì viết hàng ngàn dòng code vào một file duy nhất, người ta thường chia nhỏ ra. Đó là lý do bạn thấy lệnh `\input{}` trong file `BigData_Midterm_Group11.tex`:

```latex
\input{report/1_Introduction}
\input{report/2_Dataset}
```
Lệnh `\input{đường_dẫn_file}` sẽ "bê" toàn bộ nội dung của file đó đắp vào vị trí hiện tại. Điều này giúp bạn dễ dàng quản lý, phân công cho các thành viên trong nhóm (mỗi người viết 1 file `.tex` riêng).

---

## 5. Mẹo khắc phục lỗi (Troubleshooting)
Khi bấm Compile mà bị lỗi (báo đỏ), đừng hoảng sợ:
1. **Quên đóng ngoặc:** Kiểm tra xem các lệnh `\begin{...}` đã có `\end{...}` tương ứng chưa. Các dấu `{` đã có `}` đóng lại chưa.
2. **Ký tự đặc biệt:** Các ký tự như `%`, `$`, `&`, `#`, `_` là ký tự dành riêng cho hệ thống LaTeX. Nếu bạn muốn in chúng ra văn bản bình thường, phải thêm dấu `\` đằng trước. Ví dụ: `100\%`, `\$50`.
3. **Lỗi tiếng Việt:** Đảm bảo file chính của bạn có khai báo `\usepackage[utf8]{inputenc}` và `\usepackage[T5]{fontenc}` (hoặc `\usepackage{vietnam}`).

Chúc bạn làm quen với LaTeX thành công! Mới đầu có thể hơi ngợp, nhưng khi quen rồi bạn sẽ thấy văn bản làm ra cực kỳ đẹp và chuyên nghiệp.