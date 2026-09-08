package com.sentinel.rbac.repository;

import com.sentinel.auth.model.Role;
import com.sentinel.rbac.model.Permission;
import com.sentinel.rbac.model.RolePermission;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RolePermissionRepository extends JpaRepository<RolePermission, Long> {

    List<RolePermission> findByRole(Role role);

    boolean existsByRoleAndPermission(Role role, Permission permission);
}