"""
계산 로직 모듈
- Subject: 과목 데이터클래스
- StudyTask: 할 일 데이터클래스
- StudyScheduler: 우선순위 계산 + 스케줄 생성
"""

import datetime as dt
from dataclasses import dataclass, field
from typing import Optional

from constants import WEIGHTS, REVIEW_TABLE


# --------------------------------------------
# 데이터클래스
# --------------------------------------------
@dataclass
class Subject:                                  # 과목 정보
    name: str
    procrastination_level: int
    difficulty: int
    volume: int
    is_major: bool
    exam_date: Optional[dt.datetime] = None

    urgency_val: float = 3.0
    total_score: float = 0.0
    weight_ratio: float = 0.0
    allocated_hours: float = 0.0

    def calculate_subject_score(self) -> float:         # 과목의 최종 점수 계산
        interest_val = 6 - self.procrastination_level
        major_val = 5 if self.is_major else 1
        self.total_score = (
            self.urgency_val * WEIGHTS["urgency"]
            + self.volume * WEIGHTS["volume"]
            + self.difficulty * WEIGHTS["difficulty"]
            + interest_val * WEIGHTS["interest"]
            + major_val * WEIGHTS["major"]
        )
        return self.total_score


@dataclass                      # 할 일
class StudyTask:
    name: str
    task_type: str
    review_hours: float
    study_hours: float
    hours: float


# --------------------------------------------
# 스케줄러
# --------------------------------------------
@dataclass
class StudyScheduler:               # 과목 우선순위 계산 + 날짜별 공부 스케줄
    today_date: dt.date
    daily_hours: float
    subjects: list = field(default_factory=list)
    daily_plan: dict = field(default_factory=dict)

    def add_subject(self, subject: Subject) -> None:    # 스케줄러에 과목 추가
        self.subjects.append(subject)

    def calculate_priority(self) -> None:               # 과목별 우선순위와 시간 배분 계산
        if not self.subjects:
            return
        self._update_urgency_scores()
        total_sum = sum(s.calculate_subject_score() for s in self.subjects)
        for s in self.subjects:
            s.weight_ratio = (s.total_score / total_sum) * 100 if total_sum > 0 else 0
            s.allocated_hours = self.daily_hours * (s.weight_ratio / 100)
        self.subjects.sort(key=lambda s: s.total_score, reverse=True)

    def _update_urgency_scores(self) -> None:           # 시험 날짜가 가까운 과목일수록 긴급도를 높게 주는 함수
        current_dt = dt.datetime.combine(self.today_date, dt.time.min)
        hours_left = {                                  # 시험까지 남은 시간을 시간 단위로 계산
            s.name: max((s.exam_date - current_dt).total_seconds() / 3600, 0)
            for s in self.subjects if s.exam_date is not None
        }
        if not hours_left:                              # 시험 날짜가 입력된 과목이 없으면 긴급도는 기본값 3.0
            for s in self.subjects:
                s.urgency_val = 3.0
            return
        min_h, max_h = min(hours_left.values()), max(hours_left.values())
        for s in self.subjects:
            if s.name not in hours_left:
                s.urgency_val = 3.0
                continue
            h = hours_left[s.name]
            s.urgency_val = 5.0 if max_h == min_h else 5.0 - ((h - min_h) / (max_h - min_h)) * 4.0

    def _active_subjects_on(self, current_date):        # 특정 날짜에 공부해야 하는 과목 골라냄
        return [s for s in self.subjects if s.exam_date is None or current_date < s.exam_date.date()]

    def _allocate_hours(self, subjects, total_hours, digits=1):     # 공부 시간을 과목별로 비율에 맞게 나눔
        if not subjects:
            return []
        total_weight = sum(s.weight_ratio for s in subjects)
        if total_weight <= 0:
            equal = round(total_hours / len(subjects), digits)
            result = [(s, equal) for s in subjects[:-1]]
            result.append((subjects[-1], round(total_hours - sum(h for _, h in result), digits)))
            return result
        result, assigned = [], 0.0
        for i, s in enumerate(subjects):
            hours = (round(total_hours * (s.weight_ratio / total_weight), digits)
                    if i < len(subjects) - 1
                    else round(total_hours - assigned, digits))
            assigned += hours
            result.append((s, hours))
        return result

    def generate_schedule(self, plan_days: int = 14) -> None:   # 날짜별 학습 스케줄 생성
        self.daily_plan.clear()
        start_date = self.today_date + dt.timedelta(days=1)
        for day_offset in range(plan_days):
            current_date = start_date + dt.timedelta(days=day_offset)
            active = self._active_subjects_on(current_date)
            if not active:
                continue
            if day_offset in REVIEW_TABLE:
                tasks = self._build_review_day_tasks(active, day_offset)
            else:
                label = "신규학습" if day_offset == 0 else "학습"
                tasks = self._build_normal_day_tasks(active, label)
            self.daily_plan[current_date] = tasks

    def _build_normal_day_tasks(self, subjects, label):     # 일반 학습일 스케줄
        tasks = []
        for s, h in self._allocate_hours(subjects, self.daily_hours, 1):
            tasks.append(StudyTask(s.name, label, 0.0, h, h))
        return tasks

    def _build_review_day_tasks(self, subjects, day_offset):    # 복습일 스케줄
        ratio = REVIEW_TABLE[day_offset]
        review_map = {s.name: round(s.allocated_hours * ratio, 2) for s in subjects}
        total_review = sum(review_map.values())
        remaining = max(self.daily_hours - total_review, 0)
        study_alloc = {s.name: h for s, h in self._allocate_hours(subjects, remaining, 1)}
        tasks = []
        for s in subjects:
            r, st = review_map[s.name], study_alloc.get(s.name, 0.0)
            tasks.append(StudyTask(s.name, f"복습({day_offset}일차)", r, st, round(r + st, 1)))
        if tasks:
            assigned = sum(t.hours for t in tasks[:-1])
            tasks[-1].hours = round(self.daily_hours - assigned, 1)
            tasks[-1].study_hours = round(tasks[-1].hours - tasks[-1].review_hours, 1)
        return tasks
