package com.bugless;

import com.qasdk.constant.IBuglessEntry;
import android.content.Context;
import android.widget.Toast;
import android.os.Looper;

/**
 * Created by chivyzhuang on 14-3-26.
 * Don't change two follow lines(class name and name of method 'onEnter'):
 * ----------------------------------------------------------------
 * public class Entry implements IBuglessEntry {
 * public boolean onEnter(Context context) {
 * ----------------------------------------------------------------
 * 这个类的类名和方法'onEnter'的名字不要修改，其他可以任意添加改动
 */
public class Entry implements IBuglessEntry {

    @Override
    public boolean onEnter(Context context) {
        // Add your code here...
        // 在这里添加代码
		
        // This function will run in a separate thread
        // so that if you want to invoke some function associated with UI,
        // remember Looper. However, this will lead to that execution of repair
        // intrupt. You can do this by creating another thread.
        // 这个方法是运行在另一个线程的，所以当你要调用跟UI相关的函数时，可以用Looper去改变这个
        // 线程，但是一旦这么做，这个线程就无法继续执行后面的代码了（loop()之后），所以如果确实需要
        // 就另开一条线程来完成吧。
        /*
        Looper.prepare();
        Toast.makeText(context, "Dex file", Toast.LENGTH_SHORT).show();
        Looper.loop();
        */

        // At the end return the result: true for success and false for fail
        // 在最后面返回执行结果，true是执行成功，false是失败，这个有助于决定后面的修复工作是否继续执行
        return true;
    }
}
