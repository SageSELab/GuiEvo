package xyz.zedler.patrick.grocy.fragment.bottomSheetDialog;

/*
    This file is part of Grocy Android.

    Grocy Android is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Grocy Android is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Grocy Android.  If not, see <http://www.gnu.org/licenses/>.

    Copyright 2020 by Patrick Zedler & Dominic Zedler
*/

import android.app.Dialog;
import android.os.Bundle;
import android.text.InputType;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.TextView;

import androidx.annotation.NonNull;

import com.google.android.material.bottomsheet.BottomSheetDialog;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputLayout;

import xyz.zedler.patrick.grocy.R;
import xyz.zedler.patrick.grocy.activity.SettingsActivity;
import xyz.zedler.patrick.grocy.util.Constants;
import xyz.zedler.patrick.grocy.util.NumUtil;

public class SettingInputBottomSheetDialogFragment extends CustomBottomSheetDialogFragment {

    private final static String TAG = "SettingInputBottomSheet";

    private SettingsActivity activity;

    private EditText editText;

    @NonNull
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        return new BottomSheetDialog(requireContext(), R.style.Theme_Grocy_BottomSheetDialog);
    }

    @Override
    public View onCreateView(
            @NonNull LayoutInflater inflater,
            ViewGroup container,
            Bundle savedInstanceState
    ) {
        View view = inflater.inflate(
                R.layout.fragment_bottomsheet_setting_input, container, false
        );

        activity = (SettingsActivity) getActivity();
        Bundle bundle = getArguments();
        assert activity != null && bundle != null;

        String type = bundle.getString(Constants.ARGUMENT.TYPE);
        if(type == null) dismiss();
        assert type != null;

        // INITIALIZE VIEWS

        TextView textViewTitle = view.findViewById(R.id.text_setting_input_title);

        TextInputLayout textInput = view.findViewById(R.id.text_input_setting_input);
        editText = textInput.getEditText();
        assert editText != null;
        editText.setInputType(
                type.equals(Constants.PREF.STOCK_EXPIRING_SOON_DAYS)
                        ? InputType.TYPE_CLASS_NUMBER
                        : InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL
        );

        view.findViewById(R.id.button_setting_input_more).setOnClickListener(v -> {
            if(editText.getText().toString().isEmpty()) {
                editText.setText(String.valueOf(1));
            } else {
                double amountNew = Double.parseDouble(editText.getText().toString()) + 1;
                editText.setText(NumUtil.trim(amountNew));
            }
        });

        view.findViewById(R.id.button_setting_input_less).setOnClickListener(v -> {
            if(!editText.getText().toString().isEmpty()) {
                double amountNew = Double.parseDouble(editText.getText().toString()) - 1;
                if(amountNew >= 0) {
                    editText.setText(NumUtil.trim(amountNew));
                }
            }
        });

        MaterialButton buttonClear = view.findViewById(R.id.button_setting_input_clear);
        buttonClear.setOnClickListener(v -> {
            editText.setText(null);
            textInput.clearFocus();
            activity.hideKeyboard();
        });

        view.findViewById(R.id.button_setting_input_save).setOnClickListener(v -> {
            switch (type) {
                case Constants.PREF.STOCK_EXPIRING_SOON_DAYS:
                    if(editText.getText().toString().isEmpty()) {
                        textInput.setError(activity.getString(R.string.error_empty));
                        return;
                    } else {
                        textInput.setErrorEnabled(false);
                    }
                    activity.setExpiringSoonDays(editText.getText().toString());
                    break;
                case Constants.PREF.STOCK_DEFAULT_PURCHASE_AMOUNT:
                    activity.setAmountPurchase(editText.getText().toString());
                    break;
                case Constants.PREF.STOCK_DEFAULT_CONSUME_AMOUNT:
                    activity.setAmountConsume(editText.getText().toString());
                    break;
                case Constants.PREF.SHOPPING_MODE_UPDATE_INTERVAL:
                    activity.setUpdateInterval(editText.getText().toString());
                    break;
            }
            dismiss();
        });

        String title = null;
        String hint = null;
        String input = null;
        switch (type) {
            case Constants.PREF.STOCK_EXPIRING_SOON_DAYS:
                title = activity.getString(R.string.setting_expiring_soon_days);
                hint = "Days";
                input = bundle.getString(Constants.PREF.STOCK_EXPIRING_SOON_DAYS);
                buttonClear.setText(activity.getString(R.string.action_reset));
                buttonClear.setOnClickListener(v -> {
                    editText.setText(String.valueOf(5));
                    textInput.setErrorEnabled(false);
                    textInput.clearFocus();
                    activity.hideKeyboard();
                });
                break;
            case Constants.PREF.STOCK_DEFAULT_PURCHASE_AMOUNT:
                title = activity.getString(R.string.setting_default_amount_purchase);
                hint = activity.getString(R.string.property_amount);
                input = bundle.getString(Constants.PREF.STOCK_DEFAULT_PURCHASE_AMOUNT);
                break;
            case Constants.PREF.STOCK_DEFAULT_CONSUME_AMOUNT:
                title = activity.getString(R.string.setting_default_amount_consume);
                hint = activity.getString(R.string.property_amount);
                input = bundle.getString(Constants.PREF.STOCK_DEFAULT_CONSUME_AMOUNT);
                break;
            case Constants.PREF.SHOPPING_MODE_UPDATE_INTERVAL:
                title = activity.getString(R.string.setting_shopping_mode_update_interval);
                hint = activity.getString(R.string.property_seconds);
                input = bundle.getString(Constants.PREF.SHOPPING_MODE_UPDATE_INTERVAL);
                break;
        }

        textViewTitle.setText(title);

        textInput.setHint(hint);

        editText.setText(input == null || input.isEmpty() || input.equals("null") ? null : input);

        return view;
    }

    @NonNull
    @Override
    public String toString() {
        return TAG;
    }
}
