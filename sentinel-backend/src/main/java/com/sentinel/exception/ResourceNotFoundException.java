package com.sentinel.exception;

public class ResourceNotFoundException extends SentinelException {

    public ResourceNotFoundException(String resource, Object id) {
        super("RESOURCE_NOT_FOUND", resource + " not found with id: " + id);
    }

    public ResourceNotFoundException(String message) {
        super("RESOURCE_NOT_FOUND", message);
    }
}