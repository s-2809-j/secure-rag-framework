package com.sentinel.fastapi.exception;

public class FastApiException extends RuntimeException {

    public FastApiException(String message) {
        super(message);
    }

    public FastApiException(String message, Throwable cause) {
        super(message, cause);
    }
}