"""
GUI 애플리케이션 + 실행 진입점
- SchedulerApp: tkinter 기반 GUI
"""

import datetime as dt
from typing import Optional

import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from constants import WEEKDAY_KR
from scheduler_core import Subject, StudyScheduler

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# -------------------------------
# GUI 애플리케이션
# -------------------------------
class SchedulerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("셤포터즈: 지능형 시험공부 스케줄러")
        self.geometry("1100x750")
        self.configure(bg="#f5f5f7")

        self.subjects: list[Subject] = []
        self.scheduler: Optional[StudyScheduler] = None

        self._build_style()
        self._build_layout()

    # ---------- 스타일 ----------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TLabel", background="#f5f5f7", font=("Malgun Gothic", 10))
        style.configure("TButton", font=("Malgun Gothic", 10), padding=6)
        style.configure("Header.TLabel", font=("Malgun Gothic", 14, "bold"), background="#f5f5f7")
        style.configure("Sub.TLabel", font=("Malgun Gothic", 11, "bold"), background="#f5f5f7", foreground="#333")
        style.configure("Treeview", font=("Malgun Gothic", 9), rowheight=24)
        style.configure("Treeview.Heading", font=("Malgun Gothic", 10, "bold"))

    # ---------- 레이아웃 ----------
    def _build_layout(self):
        header = ttk.Label(self, text=" 셤포터즈: 지능형 시험공부 스케줄러", style="Header.TLabel")
        header.pack(pady=10)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_input = ttk.Frame(notebook)
        self.tab_priority = ttk.Frame(notebook)
        self.tab_schedule = ttk.Frame(notebook)
        self.tab_chart = ttk.Frame(notebook)

        notebook.add(self.tab_input, text="① 입력")
        notebook.add(self.tab_priority, text="② 우선순위")
        notebook.add(self.tab_schedule, text="③ 학습 스케줄")
        notebook.add(self.tab_chart, text="④ 한 눈에 보기")

        self._build_input_tab()
        self._build_priority_tab()
        self._build_schedule_tab()
        self._build_chart_tab()

    # ---------- ① 입력 탭 ----------
    def _build_input_tab(self):
        frame = self.tab_input

        # 상단: 의사결정 매트릭스 안내
        info_frame = ttk.LabelFrame(frame, text="의사결정 매트릭스 안내")
        info_frame.pack(fill="x", padx=10, pady=(10, 5))

        info_text = tk.Text(
            info_frame, height=8, font=("Malgun Gothic", 9),
            bg="#faf9d9", relief="flat", wrap="none",
        )
        info_text.pack(fill="x", padx=8, pady=8)

        matrix_rows = [
            ("긴급도", "10", "시험이 가까울수록 높은 점수예요."),
            ("분량", "4", "공부할 내용이 많을수록 높은 점수예요. (1~5)"),
            ("난이도", "3", "어렵다고 느낄수록 높은 점수예요. (1~5)"),
            ("흥미도", "2", "미루고 싶을수록 낮은 점수로 반영돼요."),
            ("전공여부", "2", "전공 과목이면 더 높은 점수를 받아요."),
        ]
        for attr, weight, desc in matrix_rows:
            info_text.insert("end", f"  {attr}: {weight}   ({desc})\n")
        info_text.insert("end", "\n  ✨ 총점이 높을수록 우선순위가 높아져요. ")

        info_text.tag_add("header", "1.0", "1.end")
        info_text.tag_configure("header", font=("Malgun Gothic", 9, "bold"), foreground="#c71e12")
        info_text.config(state="disabled")

        # 본문 영역
        body = ttk.Frame(frame)
        body.pack(fill="both", expand=True)

        # 좌측
        left = ttk.Frame(body)
        left.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(left, text="📅 기본 설정", style="Sub.TLabel").pack(anchor="w", pady=(0, 5))

        basic = ttk.LabelFrame(left, text="오늘 날짜 / 학습 시간 / 기간")
        basic.pack(fill="x", pady=5)

        today = dt.date.today()
        ttk.Label(basic, text="오늘 날짜 (MM/DD):").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.entry_today = ttk.Entry(basic, width=15)
        self.entry_today.insert(0, today.strftime("%m/%d"))
        self.entry_today.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(basic, text="하루 학습시간 (h):").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.entry_hours = ttk.Entry(basic, width=15)
        self.entry_hours.insert(0, "6")
        self.entry_hours.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(basic, text="스케줄 기간 (일):").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.entry_plan_days = ttk.Entry(basic, width=15)
        self.entry_plan_days.insert(0, "14")
        self.entry_plan_days.grid(row=2, column=1, padx=5, pady=4)

        # 과목 입력 폼
        ttk.Label(left, text="✔ 과목 추가", style="Sub.TLabel").pack(anchor="w", pady=(15, 5))
        subj_frame = ttk.LabelFrame(left, text="과목 정보")
        subj_frame.pack(fill="x", pady=5)

        ttk.Label(subj_frame, text="과목명:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.entry_name = ttk.Entry(subj_frame, width=20)
        self.entry_name.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(subj_frame, text="미루고 싶은 정도 (1~5):").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.spin_procrast = ttk.Spinbox(subj_frame, from_=1, to=5, width=18)
        self.spin_procrast.set(3)
        self.spin_procrast.grid(row=1, column=1, padx=5, pady=3)

        ttk.Label(subj_frame, text="난이도 (1~5):").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.spin_diff = ttk.Spinbox(subj_frame, from_=1, to=5, width=18)
        self.spin_diff.set(3)
        self.spin_diff.grid(row=2, column=1, padx=5, pady=3)

        ttk.Label(subj_frame, text="분량 (1~5):").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        self.spin_vol = ttk.Spinbox(subj_frame, from_=1, to=5, width=18)
        self.spin_vol.set(3)
        self.spin_vol.grid(row=3, column=1, padx=5, pady=3)

        self.var_major = tk.BooleanVar(value=False)
        ttk.Checkbutton(subj_frame, text="전공 과목", variable=self.var_major).grid(
            row=4, column=0, columnspan=2, sticky="w", padx=5, pady=3
        )

        ttk.Label(subj_frame, text="시험 일시 (MM/DD HH:MM, 선택):").grid(row=5, column=0, sticky="w", padx=5, pady=3)
        self.entry_exam = ttk.Entry(subj_frame, width=20)
        self.entry_exam.grid(row=5, column=1, padx=5, pady=3)

        ttk.Button(left, text="➕ 과목 추가", command=self.on_add_subject).pack(fill="x", pady=8)
        ttk.Button(left, text="🚀 우선순위 / 스케줄 계산", command=self.on_calculate).pack(fill="x", pady=2)

        # 우측
        right = ttk.Frame(body)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ttk.Label(right, text="📄 등록된 과목", style="Sub.TLabel").pack(anchor="w")

        cols = ("이름", "미루기", "난이도", "분량", "전공", "시험일시")
        self.tree_subjects = ttk.Treeview(right, columns=cols, show="headings", height=18)
        for c, w in zip(cols, (140, 70, 70, 60, 60, 130)):
            self.tree_subjects.heading(c, text=c)
            self.tree_subjects.column(c, width=w, anchor="center")
        self.tree_subjects.pack(fill="both", expand=True, pady=(0, 5))

        button_frame = ttk.Frame(right)
        button_frame.pack(fill="x", pady=5)

        ttk.Button(button_frame, text="선택 과목 삭제 (Ctrl로 다수 선택)",
                   command=self.on_delete_subject).pack(side="left", padx=2)
        ttk.Button(button_frame, text="모두 삭제",
                   command=self.on_delete_all_subjects).pack(side="left", padx=2)

    # ---------- ② 우선순위 탭 ----------
    def _build_priority_tab(self):
        ttk.Label(self.tab_priority, text="📌 우선순위 계산 결과",
                  style="Sub.TLabel").pack(anchor="w", padx=10, pady=10)

        cols = ("순위", "과목명", "총점", "긴급도", "비중(%)", "일배분(h)", "시험일시")
        self.tree_priority = ttk.Treeview(self.tab_priority, columns=cols, show="headings", height=15)
        for c, w in zip(cols, (60, 160, 90, 80, 90, 100, 140)):
            self.tree_priority.heading(c, text=c)
            self.tree_priority.column(c, width=w, anchor="center")
        self.tree_priority.pack(fill="both", expand=True, padx=10, pady=5)

        self.lbl_priority_info = ttk.Label(self.tab_priority, text="", style="TLabel")
        self.lbl_priority_info.pack(anchor="w", padx=10, pady=5)

    # ---------- ③ 스케줄 탭 ----------
    def _build_schedule_tab(self):
        ttk.Label(
            self.tab_schedule,
            text="📅 에빙하우스 망각곡선 기반 학습 스케줄 (복습: 1·3·7·14일)",
            style="Sub.TLabel"
        ).pack(anchor="w", padx=10, pady=10)

        cols = ("날짜", "요일", "과목", "유형", "복습(h)", "학습(h)", "합계(h)")
        self.tree_schedule = ttk.Treeview(self.tab_schedule, columns=cols, show="headings", height=20)
        for c, w in zip(cols, (90, 60, 160, 110, 80, 80, 80)):
            self.tree_schedule.heading(c, text=c)
            self.tree_schedule.column(c, width=w, anchor="center")
        self.tree_schedule.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_schedule.tag_configure("review", background="#fff4d6")
        self.tree_schedule.tag_configure("daysep", background="#e8eef7")

    # ---------- ④ 차트 탭 ----------
    def _build_chart_tab(self):
        ttk.Label(self.tab_chart, text="🎨 한 눈에 보기",
                  style="Sub.TLabel").pack(anchor="w", padx=10, pady=10)
        self.chart_container = ttk.Frame(self.tab_chart)
        self.chart_container.pack(fill="both", expand=True, padx=10, pady=5)
        self.canvas = None

    # =====================================================
    # 이벤트 핸들러
    # =====================================================
    def on_add_subject(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("입력 오류", "과목명을 입력해 주세요!")
            return
        try:
            procrast = int(self.spin_procrast.get())
            diff = int(self.spin_diff.get())
            vol = int(self.spin_vol.get())
            for v, label in [(procrast, "미루기"), (diff, "난이도"), (vol, "분량")]:
                if not (1 <= v <= 5):
                    raise ValueError(f"{label}는 1~5 사이여야 합니다.")
        except ValueError as e:
            messagebox.showerror("입력 오류", str(e))
            return

        is_major = self.var_major.get()
        exam_date = None
        exam_text = self.entry_exam.get().strip()
        if exam_text:
            try:
                today = self._parse_today()
                date_part, time_part = exam_text.split()
                month, day = map(int, date_part.split("/"))
                hour, minute = map(int, time_part.split(":"))
                exam_date = dt.datetime(today.year, month, day, hour, minute)
                if exam_date.date() < today:
                    exam_date = exam_date.replace(year=today.year + 1)
            except Exception:
                messagebox.showwarning("입력 오류", "시험 일시 형식: MM/DD HH:MM\n예: 06/15 09:00")
                return

        subject = Subject(
            name=name,
            procrastination_level=procrast,
            difficulty=diff,
            volume=vol,
            is_major=is_major,
            exam_date=exam_date,
        )
        self.subjects.append(subject)

        exam_str = exam_date.strftime("%m/%d %H:%M") if exam_date else "미정"
        self.tree_subjects.insert(
            "", "end",
            values=(name, procrast, diff, vol, "예" if is_major else "아니오", exam_str)
        )

        # 입력란 초기화
        self.entry_name.delete(0, "end")
        self.entry_exam.delete(0, "end")
        self.spin_procrast.set(3)
        self.spin_diff.set(3)
        self.spin_vol.set(3)
        self.var_major.set(False)

    def on_delete_subject(self):
        selected_items = self.tree_subjects.selection()
        if not selected_items:
            messagebox.showinfo("안내", "삭제할 과목을 선택해 주세요.")
            return

        count = len(selected_items)
        if not messagebox.askyesno("삭제 확인", f"{count}개의 과목을 삭제하시겠습니까?"):
            return

        deleted_names = []
        for item in selected_items:
            values = self.tree_subjects.item(item)['values']
            deleted_names.append(values[0])

        self.subjects = [s for s in self.subjects if s.name not in deleted_names]
        for item in selected_items:
            self.tree_subjects.delete(item)

        messagebox.showinfo("완료", f"{count}개의 과목이 삭제되었습니다.")

    def on_delete_all_subjects(self):
        if not self.subjects:
            messagebox.showinfo("안내", "삭제할 과목이 없습니다.")
            return
        if messagebox.askyesno("삭제 확인", "정말로 모든 과목을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다."):
            self.subjects.clear()
            self.tree_subjects.delete(*self.tree_subjects.get_children())
            messagebox.showinfo("완료", "모든 과목이 삭제되었습니다.")

    def on_calculate(self):
        if not self.subjects:
            messagebox.showinfo("안내", "과목을 1개 이상 추가해 주세요!")
            return
        try:
            today = self._parse_today()
            daily_hours = float(self.entry_hours.get())
            plan_days = int(self.entry_plan_days.get())
        except ValueError:
            messagebox.showerror("입력 오류", "기본 설정 값을 확인해 주세요.")
            return

        self.scheduler = StudyScheduler(today_date=today, daily_hours=daily_hours)
        for s in self.subjects:
            self.scheduler.add_subject(s)

        self.scheduler.calculate_priority()
        self.scheduler.generate_schedule(plan_days)

        self._render_priority()
        self._render_schedule()
        self._render_chart()

        messagebox.showinfo("완료", "계산이 끝났어요! 상단 탭에서 결과를 확인해 주세요.")

    # =====================================================
    # 렌더링
    # =====================================================
    def _parse_today(self) -> dt.date:
        text = self.entry_today.get().strip()
        month, day = map(int, text.split("/"))
        return dt.date(dt.date.today().year, month, day)

    def _render_priority(self):
        for row in self.tree_priority.get_children():
            self.tree_priority.delete(row)
        for i, s in enumerate(self.scheduler.subjects, start=1):
            exam_str = s.exam_date.strftime("%m/%d %H:%M") if s.exam_date else "미정"
            self.tree_priority.insert(
                "", "end",
                values=(
                    i, s.name,
                    f"{s.total_score:.2f}",
                    f"{s.urgency_val:.2f}",
                    f"{s.weight_ratio:.1f}",
                    f"{s.allocated_hours:.1f}",
                    exam_str,
                )
            )
        self.lbl_priority_info.config(
            text=f"💡하루 {self.scheduler.daily_hours}시간을 의사결정 매트릭스 기준으로 과목별로 배분했어요!"
        )

    def _render_schedule(self):
        for row in self.tree_schedule.get_children():
            self.tree_schedule.delete(row)

        for date in sorted(self.scheduler.daily_plan):
            tasks = self.scheduler.daily_plan[date]
            weekday = WEEKDAY_KR[date.weekday()]
            is_review = any("복습" in t.task_type for t in tasks)
            tag = "review" if is_review else ""

            for idx, t in enumerate(tasks):
                self.tree_schedule.insert(
                    "", "end",
                    values=(
                        date.strftime("%m/%d") if idx == 0 else "",
                        weekday if idx == 0 else "",
                        t.name,
                        t.task_type,
                        f"{t.review_hours:.1f}" if t.review_hours > 0 else "-",
                        f"{t.study_hours:.1f}" if t.study_hours > 0 else "-",
                        f"{t.hours:.1f}",
                    ),
                    tags=(tag,)
                )
            total = sum(t.hours for t in tasks)
            self.tree_schedule.insert(
                "", "end",
                values=("", "", "▶ 합계", "", "", "", f"{total:.1f}"),
                tags=("daysep",)
            )

    def _render_chart(self):
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(8, 6), dpi=100)
        ax1 = fig.add_subplot(1, 1, 1)

        names = [s.name for s in self.scheduler.subjects]
        ratios = [s.weight_ratio for s in self.scheduler.subjects]
        ax1.pie(ratios, labels=names, autopct="%1.1f%%",
                startangle=140, colors=plt.cm.Pastel1.colors)
        ax1.set_title(f"과목별 학습 시간 비중 (총 {self.scheduler.daily_hours}h/일)")

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


# -------------------------------
# 실행
# -------------------------------
if __name__ == "__main__":
    app = SchedulerApp()
    app.mainloop()
