#!/usr/bin/env python3
# reset_proxy.py

import logging
import os
import subprocess
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("proxy_reset")

def check_current_proxies():
    """Проверка текущих настроек прокси в окружении"""
    proxy_vars = [
        "http_proxy", "https_proxy", "no_proxy",
        "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY"
    ]
    
    logger.info("Текущие настройки прокси:")
    for var in proxy_vars:
        value = os.environ.get(var, "не установлен")
        logger.info(f"  {var}: {value}")
    
    return {var: os.environ.get(var) for var in proxy_vars if os.environ.get(var)}

def clear_proxy_settings():
    """Очистка всех переменных окружения, связанных с прокси"""
    proxy_vars = [
        "http_proxy", "https_proxy", "no_proxy",
        "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY"
    ]
    
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]
            logger.info(f"Удалена переменная окружения: {var}")

def check_system_network():
    """Проверка сетевой конфигурации системы"""
    try:
        logger.info("Проверка файла /etc/resolv.conf:")
        with open("/etc/resolv.conf", "r") as f:
            resolv_conf = f.read()
            logger.info(resolv_conf)
    except Exception as e:
        logger.error(f"Ошибка при чтении /etc/resolv.conf: {e}")
    
    try:
        logger.info("Выполнение команды ip route:")
        route_output = subprocess.check_output(["ip", "route"]).decode("utf-8")
        logger.info(route_output)
    except Exception as e:
        logger.error(f"Ошибка при выполнении ip route: {e}")
    
    try:
        logger.info("Выполнение команды ifconfig:")
        ifconfig_output = subprocess.check_output(["ifconfig"]).decode("utf-8")
        logger.info(ifconfig_output)
    except Exception as e:
        logger.error(f"Ошибка при выполнении ifconfig: {e}")

def main():
    """Основная функция для проверки и сброса прокси-настроек"""
    logger.info("=== Запуск проверки и сброса настроек прокси ===")
    
    # Проверяем текущие настройки
    proxies = check_current_proxies()
    
    # Сохраняем старые настройки
    proxies_backup = proxies.copy()
    
    # Проверяем сетевую конфигурацию
    check_system_network()
    
    # Очищаем настройки прокси
    clear_proxy_settings()
    logger.info("Настройки прокси очищены")
    
    # Запрашиваем подтверждение на восстановление
    restore = input("Восстановить исходные настройки прокси? (y/n): ").lower().strip() == 'y'
    
    if restore:
        # Восстанавливаем настройки прокси
        for var, value in proxies_backup.items():
            if value:
                os.environ[var] = value
                logger.info(f"Восстановлена переменная окружения: {var}={value}")
        
        logger.info("Настройки прокси восстановлены")
    else:
        logger.info("Настройки прокси оставлены очищенными")
    
    logger.info("=== Завершение проверки и сброса настроек прокси ===")

if __name__ == "__main__":
    main() 