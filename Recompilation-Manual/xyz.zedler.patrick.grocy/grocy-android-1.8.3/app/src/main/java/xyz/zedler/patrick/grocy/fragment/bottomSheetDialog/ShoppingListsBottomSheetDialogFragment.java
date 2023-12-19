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

import android.app.Activity;
import android.app.Dialog;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.DefaultItemAnimator;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.bottomsheet.BottomSheetDialog;

import java.util.ArrayList;

import xyz.zedler.patrick.grocy.R;
import xyz.zedler.patrick.grocy.activity.MainActivity;
import xyz.zedler.patrick.grocy.activity.ShoppingActivity;
import xyz.zedler.patrick.grocy.adapter.ShoppingListAdapter;
import xyz.zedler.patrick.grocy.fragment.ShoppingListFragment;
import xyz.zedler.patrick.grocy.fragment.ShoppingListItemEditFragment;
import xyz.zedler.patrick.grocy.model.ShoppingList;
import xyz.zedler.patrick.grocy.util.Constants;
import xyz.zedler.patrick.grocy.view.ActionButton;

public class ShoppingListsBottomSheetDialogFragment extends CustomBottomSheetDialogFragment
        implements ShoppingListAdapter.ShoppingListAdapterListener {

    private final static String TAG = "ShoppingListsBottomSheet";

    private Activity activity;
    private ArrayList<ShoppingList> shoppingLists;

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
                R.layout.fragment_bottomsheet_list_selection, container, false
        );

        activity = getActivity();
        Bundle bundle = getArguments();
        assert activity != null && bundle != null;

        shoppingLists = bundle.getParcelableArrayList(Constants.ARGUMENT.SHOPPING_LISTS);
        int selected = bundle.getInt(Constants.ARGUMENT.SELECTED_ID, -1);

        TextView textViewTitle = view.findViewById(R.id.text_list_selection_title);
        textViewTitle.setText(activity.getString(R.string.property_shopping_lists));

        RecyclerView recyclerView = view.findViewById(R.id.recycler_list_selection);
        recyclerView.setLayoutManager(
                new LinearLayoutManager(
                        activity,
                        LinearLayoutManager.VERTICAL,
                        false
                )
        );
        recyclerView.setItemAnimator(new DefaultItemAnimator());
        recyclerView.setAdapter(
                new ShoppingListAdapter(
                        shoppingLists, selected, this
                )
        );

        ActionButton buttonNew = view.findViewById(R.id.button_list_selection_new);
        if(!bundle.getBoolean(Constants.ARGUMENT.SHOW_OFFLINE)) {
            buttonNew.setVisibility(View.VISIBLE);
            buttonNew.setOnClickListener(v -> {
                if(activity.getClass() != MainActivity.class) return;
                MainActivity activity = (MainActivity) this.activity;
                dismiss();
                Bundle bundle1 = new Bundle();
                bundle1.getString(Constants.ARGUMENT.TYPE, Constants.ACTION.CREATE);
                activity.replaceFragment(Constants.UI.SHOPPING_LIST_EDIT, bundle1, true);
            });
        }

        return view;
    }

    @Override
    public void onItemRowClicked(int position) {
        if(activity.getClass() == MainActivity.class) {
            Fragment currentFragment = ((MainActivity) activity).getCurrentFragment();
            if(currentFragment.getClass() == ShoppingListFragment.class) {
                ((ShoppingListFragment) currentFragment).selectShoppingList(
                        shoppingLists.get(position).getId()
                );
            } else if(currentFragment.getClass() == ShoppingListItemEditFragment.class) {
                ((ShoppingListItemEditFragment) currentFragment).selectShoppingList(
                        shoppingLists.get(position).getId()
                );
            }
        } else if(activity.getClass() == ShoppingActivity.class) {
            ((ShoppingActivity) activity).selectShoppingList(shoppingLists.get(position).getId());
        }
        dismiss();
    }

    @NonNull
    @Override
    public String toString() {
        return TAG;
    }
}
