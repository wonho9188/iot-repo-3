from typing import Dict, Any, Optional

# 컨트롤러 참조 설정
controller: Optional[Any] = None

# 컨트롤러 설정 함수
def set_controller(main_controller):
    global controller
    controller = main_controller