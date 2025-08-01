# LangSmith Debugging Suite

This suite provides comprehensive debugging tools for LangSmith tracing issues, specifically designed to help diagnose why traces are not appearing in real-time.

## 🔍 Problem Analysis

Based on your description, you're experiencing:
- Traces not appearing in real-time (only seeing 5-hour-old traces)
- Uncertainty about async function tracing with `@traceable`
- Need for better error handling and debugging

## 🛠️ Debugging Tools

### 1. `debug_langsmith.py` - Comprehensive Debugging
**Purpose**: Complete diagnostic testing of LangSmith connectivity and functionality

**Features**:
- Environment variable verification
- API connectivity testing
- LangSmith client testing
- Manual trace creation testing
- Sync and async `@traceable` testing

**Usage**:
```bash
cd api
python debug_langsmith.py
```

**Output**:
- Console summary of all tests
- `langsmith_debug.log` - Detailed logs
- `langsmith_debug_results.json` - Complete results

### 2. `test_langsmith.py` - Quick Integration Test
**Purpose**: Fast test of LangSmith integration with your processor

**Features**:
- Tests actual processor functions
- Validates both `@traceable` and manual tracing
- Quick connectivity verification

**Usage**:
```bash
cd api
python test_langsmith.py
```

### 3. `monitor_traces.py` - Real-time Trace Monitoring
**Purpose**: Monitor LangSmith traces in real-time to verify they're being created

**Features**:
- Real-time trace monitoring
- Project statistics
- Single check or continuous monitoring modes
- Detailed trace analysis

**Usage**:
```bash
cd api
python monitor_traces.py
```

**Modes**:
- **Single Check**: Analyze recent traces once
- **Continuous**: Monitor for new traces every 30 seconds

### 4. `sync_vs_async_test.py` - Async vs Sync Comparison
**Purpose**: Compare tracing behavior between synchronous and asynchronous functions

**Features**:
- Side-by-side sync/async testing
- Error handling comparison
- Nested function tracing
- Performance comparison

**Usage**:
```bash
cd api
python sync_vs_async_test.py
```

## 🔧 Enhanced Processor

### Key Improvements in `processor.py`:

1. **Comprehensive Logging**:
   - Added detailed logging throughout the process
   - Separate log file: `processor.log`
   - Real-time status updates

2. **Manual Tracing Fallback**:
   - `_create_manual_trace()` - Creates traces manually when `@traceable` fails
   - `_end_manual_trace()` - Properly ends manual traces
   - Automatic fallback for both `@traceable` and manual methods

3. **Enhanced Error Handling**:
   - Better error capture and reporting
   - Trace error logging
   - Graceful degradation

4. **Environment Variable Validation**:
   - Startup validation of all LangSmith settings
   - Clear error messages for missing configuration

## 🚀 Step-by-Step Debugging Process

### Step 1: Environment Verification
```bash
cd api
python debug_langsmith.py
```

**Check for**:
- ✅ All environment variables set
- ✅ API connectivity successful
- ✅ Client test successful

**If failing**: Check your `.env` file and API key

### Step 2: Basic Tracing Test
```bash
python sync_vs_async_test.py
```

**Check for**:
- ✅ Both sync and async tests complete
- ✅ No errors in execution
- Review logs for any tracing issues

### Step 3: Real-time Monitoring
```bash
python monitor_traces.py
```

**Select option 1** for single check to see recent traces

**If no traces found**:
- Run a test while monitoring is active
- Check if traces appear with delay

### Step 4: Integration Testing
```bash
python test_langsmith.py
```

**This will**:
- Test your actual processor functions
- Verify end-to-end tracing
- Provide specific recommendations

### Step 5: Live Application Testing
1. Start your FastAPI server
2. In another terminal, run continuous monitoring:
   ```bash
   python monitor_traces.py
   # Select option 2 for continuous monitoring
   ```
3. Make a request to your `/code` endpoint
4. Watch for traces appearing in real-time

## 🔍 Common Issues & Solutions

### Issue 1: No Traces Appearing
**Symptoms**: Monitor shows no recent traces

**Solutions**:
1. Check environment variables:
   ```bash
   echo $LANGSMITH_API_KEY
   echo $LANGSMITH_PROJECT
   echo $LANGSMITH_TRACING
   ```

2. Verify API key permissions at https://smith.langchain.com

3. Check network connectivity:
   ```bash
   curl -H "Authorization: Bearer $LANGSMITH_API_KEY" https://api.smith.langchain.com/sessions
   ```

### Issue 2: Async Functions Not Tracing
**Symptoms**: Sync functions trace but async don't

**Solutions**:
1. The enhanced processor now includes manual tracing fallbacks
2. Check logs for "Manual trace created" messages
3. Async functions should work with both `@traceable` and manual methods

### Issue 3: Delayed Trace Appearance
**Symptoms**: Traces appear hours later

**Solutions**:
1. Check if traces are being buffered
2. Verify system time synchronization
3. Manual traces should appear immediately
4. Check LangSmith service status

### Issue 4: Background Threading Issues
**Symptoms**: Traces incomplete or cut off

**Solutions**:
1. Enhanced processor uses manual tracing to avoid threading issues
2. Explicit trace ending ensures completion
3. Check logs for "Manual trace ended" messages

## 📊 Log Files

### `processor.log`
- Application-level logging
- Trace creation/completion status
- Error details

### `langsmith_debug.log`
- Detailed debugging information
- API call logs
- Environment variable status

### JSON Result Files
- `langsmith_debug_results.json` - Complete diagnostic results
- `sync_async_comparison.json` - Sync vs async test results
- `trace_monitor_results.json` - Recent trace analysis

## 🔗 Verification Steps

After running the debugging tools:

1. **Check LangSmith Dashboard**: https://smith.langchain.com
   - Look for project "tiny-backspace"
   - Verify recent trace activity

2. **Review Log Files**:
   - Check for successful trace creation
   - Look for any error messages
   - Verify API connectivity

3. **Test Real-time**:
   - Run continuous monitoring
   - Make test requests
   - Verify immediate trace appearance

## 🎯 Expected Outcomes

After implementing these fixes:

1. **Real-time Traces**: Traces should appear within seconds
2. **Complete Trace Trees**: Full workflow visibility
3. **Proper Metadata**: Timing and context information
4. **Error Handling**: Failed traces logged and reported
5. **Async Support**: Both sync and async functions traced

## 🆘 If Issues Persist

1. **Check Service Status**: https://status.langchain.com
2. **Review API Documentation**: https://docs.smith.langchain.com
3. **Check Rate Limits**: API may be throttled
4. **Contact Support**: With debug results and log files

## 📝 Additional Notes

- The enhanced processor maintains backward compatibility
- Manual tracing provides reliable fallback
- All debugging tools are safe to run in production
- Log files help with ongoing monitoring

Run the debugging suite and check the results. The combination of enhanced error handling, manual tracing fallbacks, and comprehensive logging should resolve your real-time tracing issues.