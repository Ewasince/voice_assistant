from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from voice_assistant.topic_definers.gpt.gpt_modules.i_gpt_module import IGPTModule


class YaGPTModule(IGPTModule):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://ya.ru/alisa_davay_pridumaem")
        # assert "Python" in driver.title

    def __enter__(self):
        # sleep(1)
        self.driver.get("https://ya.ru/alisa_davay_pridumaem")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def get_answer(self, text) -> str:
        elem = self.driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div[2]/div[2]/div/div[1]/div")
        elem.send_keys(text)
        elem.send_keys(Keys.RETURN)

        while True:
            is_thinking = len(self.driver.find_elements(by=By.XPATH, value="//div[text()='Алиса думает...']"))
            is_writing = len(self.driver.find_elements(by=By.XPATH, value="//div[text()='Алиса печатает...']"))

            if not is_thinking and not is_writing:
                break

        answers = self.driver.find_elements(by=By.CLASS_NAME, value="markdown-text")
        answer = answers[-1]
        return answer.text


if __name__ == "__main__":
    ym = YaGPTModule()

    with ym as y:
        res = ym.get_answer("Привет")

        res2 = ym.get_answer('Сколько букв "н" в слове "банан"?')

        res3 = ym.get_answer("Сколько будет два плюс два?")

