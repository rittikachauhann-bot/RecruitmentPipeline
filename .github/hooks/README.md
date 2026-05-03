# Guardrail Hooks Documentation

This directory contains comprehensive guardrail hooks that protect your recruitment pipeline from unintended harm. Hooks enforce safety policies across all agent operations.

## Hook Files

### 1. **pre-tool-use.json** - Block Dangerous Operations
Prevents execution of dangerous commands and operations:
- ❌ Blocks recursive file deletion (`rm -rf`, `rm -f /`)
- ⚠️ Warns before database drops (requires confirmation)
- ❌ Blocks credential exposure through pipes
- ⚠️ Gates production deployments (requires confirmation)
- ⚠️ Warns before bulk file operations
- ❌ Blocks world-readable permissions

### 2. **pre-file-edit.json** - Protect Critical Files
Protects critical configuration and secret files:
- ⚠️ Warns before editing credentials or `.env` files
- ⚠️ Warns before editing pipeline core files
- ⚠️ Warns about dependency changes
- ⚠️ Warns before database file modifications
- ❌ Blocks modifications to SETUP.md

### 3. **pre-api-call.json** - Validate External Operations
Validates and controls external API operations:
- ⚠️ Confirms before bulk email sends
- 🚦 Rate limits API calls to 10/minute with 3-request bursts
- ⚠️ Alerts on data exports (prevents candidate info exposure)
- ❌ Blocks unauthorized API endpoints

### 4. **session-start.json** - Inject Safety Context
Runs at session start to establish safety context:
- 🛡️ Displays safety briefing
- ✅ Validates environment (credentials, tokens, DB access)
- 📋 Reminds operators of key policies

### 5. **audit-trail.json** - Log Critical Operations
Logs all critical operations for compliance and debugging:
- 📝 Logs file deletions
- 📝 Logs database changes (INSERT/UPDATE/DELETE)
- 📝 Logs email campaigns
- 📝 Logs configuration changes
- 📝 Logs failed operations

### 6. **input-validation.json** - Sanitize User Input
Validates and sanitizes all input to prevent injection attacks:
- ✅ Validates email address format
- ❌ Prevents SQL injection attempts
- ✅ Validates JSON syntax
- ✅ Validates phone number format
- ✅ Validates URLs

### 7. **resource-limits.json** - Prevent Resource Exhaustion
Enforces resource limits to prevent system overload:
- 🚦 Limits concurrent processes to 5
- 📏 Limits file size to 50MB (warning) / 100MB (block)
- 💾 Monitors memory usage (warn at 1.5GB, limit 2GB)
- ⏱️ Limits API responses to 10MB with 30s timeout
- ❌ Blocks loops with >100k iterations
- ⚠️ Warns about recursion >1000 levels deep

### 8. **error-handling.json** - Graceful Failure Management
Ensures errors don't cascade into failures:
- 🔄 Automatically rolls back failed operations
- 🔄 Retries database errors (up to 3 times)
- 🔄 Retries network errors (exponential backoff, up to 5 times)
- ⚠️ Warns about permission errors
- 🧹 Cleans up on failures

## Severity Levels

- **CRITICAL** 🔴: Blocks operation immediately; requires user action to override
- **HIGH** 🟠: Requires confirmation before proceeding; non-negotiable
- **MEDIUM** 🟡: Warns user; allows continuation
- **LOW** 🟢: Informational only

## How Hooks Work

### Hook Types

1. **PreToolUse**: Fires before any tool execution; can block, warn, or throttle
2. **PreFileEdit**: Fires before file modifications; protects critical files
3. **PreAPICall**: Fires before API operations; validates requests
4. **SessionStart**: Fires at session initialization; injects context
5. **PostToolUse**: Fires after tool execution; audits or cleans up
6. **PreCommandExecution**: Fires before terminal commands; validates syntax

### Actions

- **BLOCK**: Prevents operation; non-negotiable
- **WARN**: Alerts user; requires confirmation to proceed
- **THROTTLE**: Rate-limits operation
- **LOG**: Records operation for audit trail
- **VALIDATE**: Checks input format/safety
- **MONITOR**: Tracks resource usage
- **INTERCEPT**: Handles errors gracefully
- **CLEANUP**: Removes temporary files on failure

## Configuration

To enable/disable a specific hook:
```json
"enabled": true
```

To override a hook temporarily, explicitly request in conversation:
> "Override the block-rm-rf guardrail for this one-time operation"

## Testing Hooks

### Test File Protection
```bash
# This should warn and require confirmation:
# Edit credentials.json
```

### Test Command Blocking
```bash
# This should be blocked:
# Run: rm -rf /important_directory
```

### Test Rate Limiting
```bash
# Send 15 requests rapidly; should throttle after 10:
# for i in {1..15}; do curl https://api.example.com; done
```

### Test Email Confirmation
```bash
# This should require confirmation:
# Send bulk email to 500 recipients
```

## Best Practices

1. ✅ Always backup before modifying `pipeline.json`
2. ✅ Test templates in draft before bulk sends
3. ✅ Review recipient lists before campaigns
4. ✅ Never commit credentials to version control
5. ✅ Run tests after dependency updates
6. ✅ Monitor audit logs regularly
7. ✅ Keep guardrails enabled in production

## Related Files

- `.github/hooks/rollback.sh` - Rolls back failed operations
- `.github/hooks/cleanup.sh` - Cleans up temporary files
- `.github/logs/` - Audit trail logs (30-day retention)

## Support

For questions about specific guardrails or to request exceptions, consult the conversation history or contact the security team.
