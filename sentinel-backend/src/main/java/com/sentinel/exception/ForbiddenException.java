package com.sentinel.exception;

public class ForbiddenException extends SentinelException {

    public ForbiddenException(String message) {
        super("FORBIDDEN", message);
    }
}