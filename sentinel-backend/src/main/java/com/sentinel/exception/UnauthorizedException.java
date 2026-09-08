package com.sentinel.exception;

public class UnauthorizedException extends SentinelException {

    public UnauthorizedException(String message) {
        super("UNAUTHORIZED", message);
    }
}